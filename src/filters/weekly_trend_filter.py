"""
WeeklyTrendFilter - 周趋势确认过滤器
多时间框架验证，确保日线信号与周线趋势一致
"""

import logging
from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import pandas as pd

from .base_filter import BaseFilter


@dataclass
class WeeklyTrendState:
    """周线趋势状态"""
    ticker: str
    weekly_ma20: Optional[float] = None       # 周线MA20当前值
    weekly_ma20_slope: Optional[float] = None # 周线MA20斜率
    weekly_trend: str = 'unknown'             # 'up', 'down', 'sideways', 'unknown'
    daily_trend: str = 'unknown'              # 'up', 'down', 'sideways', 'unknown'
    is_aligned: bool = False                  # 日/周趋势是否一致
    rejection_reason: Optional[str] = None    # 拒绝原因


class WeeklyTrendFilter(BaseFilter):
    """周趋势确认过滤器 - 多时间框架验证"""
    
    def __init__(self, config: dict, data_storage=None):
        """
        初始化周趋势过滤器
        
        Args:
            config: {
                'enabled': True,                    # 是否启用
                'weekly_ma_period': 20,             # 周线MA周期
                'slope_lookback_weeks': 4,          # 计算斜率的回看周数
                'min_weekly_slope': 0.0,            # 最小周线斜率（0表示要求上升）
                'require_alignment': True,          # 是否要求日/周趋势一致
                'sideways_threshold': 0.005         # 横盘判断阈值（斜率绝对值小于此值视为横盘）
            }
            data_storage: DataStorage实例，用于加载周线数据
        """
        super().__init__(config)
        self.enabled = config.get('enabled', True)
        self.weekly_ma_period = config.get('weekly_ma_period', 20)
        self.slope_lookback_weeks = config.get('slope_lookback_weeks', 4)
        self.min_weekly_slope = config.get('min_weekly_slope', 0.0)
        self.require_alignment = config.get('require_alignment', True)
        self.sideways_threshold = config.get('sideways_threshold', 0.005)
        self.data_storage = data_storage
        
        # 缓存周线数据
        self._weekly_data_cache: Dict[str, pd.DataFrame] = {}
    
    def _load_weekly_data(self, ticker: str) -> Optional[pd.DataFrame]:
        """加载周线数据"""
        if ticker in self._weekly_data_cache:
            return self._weekly_data_cache[ticker]
        
        if self.data_storage is None:
            self.logger.warning(f"未配置DataStorage，无法加载 {ticker} 周线数据")
            return None
        
        try:
            weekly_df = self.data_storage.load_stock_data(ticker, 'weekly')
            if weekly_df is not None and not weekly_df.empty:
                self._weekly_data_cache[ticker] = weekly_df
                return weekly_df
        except Exception as e:
            self.logger.debug(f"加载 {ticker} 周线数据失败: {e}")
        
        return None
    
    def _calculate_weekly_ma_slope(self, weekly_df: pd.DataFrame) -> tuple:
        """
        计算周线MA斜率
        
        Returns:
            tuple: (ma_value, slope, trend)
        """
        if weekly_df is None or len(weekly_df) < self.weekly_ma_period + self.slope_lookback_weeks:
            return None, None, 'unknown'
        
        # 计算周线MA
        weekly_ma = weekly_df['close'].rolling(window=self.weekly_ma_period).mean()
        
        if weekly_ma.isna().all():
            return None, None, 'unknown'
        
        # 获取最近的MA值用于计算斜率
        recent_ma = weekly_ma.tail(self.slope_lookback_weeks + 1)
        if recent_ma.isna().any():
            return weekly_ma.iloc[-1], None, 'unknown'
        
        ma_now = recent_ma.iloc[-1]
        ma_before = recent_ma.iloc[0]
        
        # 计算斜率（百分比变化）
        slope = (ma_now - ma_before) / ma_before if ma_before != 0 else 0
        
        # 判断趋势
        if slope > self.sideways_threshold:
            trend = 'up'
        elif slope < -self.sideways_threshold:
            trend = 'down'
        else:
            trend = 'sideways'
        
        return ma_now, slope, trend
    
    def _get_daily_trend(self, daily_df: pd.DataFrame) -> str:
        """从日线数据判断趋势方向"""
        if daily_df is None or len(daily_df) < 25:
            return 'unknown'
        
        # 使用日线MA20斜率判断
        if 'sma_20' not in daily_df.columns:
            return 'unknown'
        
        recent_ma20 = daily_df['sma_20'].tail(5)
        if recent_ma20.isna().any():
            return 'unknown'
        
        ma20_now = recent_ma20.iloc[-1]
        ma20_5d_ago = recent_ma20.iloc[0]
        slope = (ma20_now - ma20_5d_ago) / ma20_5d_ago if ma20_5d_ago != 0 else 0
        
        if slope > 0.005:
            return 'up'
        elif slope < -0.005:
            return 'down'
        else:
            return 'sideways'
    
    def _check_alignment(self, daily_trend: str, weekly_trend: str) -> tuple:
        """
        检查日/周趋势是否一致
        
        Returns:
            tuple: (is_aligned, rejection_reason)
        """
        # 如果周线趋势未知，允许通过（优雅降级）
        if weekly_trend == 'unknown':
            return True, None
        
        # 日线未知，允许通过
        if daily_trend == 'unknown':
            return True, None
        
        # 核心规则：日线上升但周线下降 = 拒绝
        if daily_trend == 'up' and weekly_trend == 'down':
            return False, f"日/周趋势冲突: 日线上升但周线下降"
        
        # 日线下降但周线上升 = 拒绝（反向操作也可能是假信号）
        if daily_trend == 'down' and weekly_trend == 'up':
            return False, f"日/周趋势冲突: 日线下降但周线上升"
        
        # 其他情况（方向一致或有一方横盘）= 允许
        return True, None
    
    def analyze_stock(self, ticker: str, daily_df: pd.DataFrame) -> WeeklyTrendState:
        """
        分析单只股票的周趋势状态
        
        Args:
            ticker: 股票代码
            daily_df: 日线数据
        
        Returns:
            WeeklyTrendState: 分析结果
        """
        state = WeeklyTrendState(ticker=ticker)
        
        # 获取日线趋势
        state.daily_trend = self._get_daily_trend(daily_df)
        
        # 加载周线数据
        weekly_df = self._load_weekly_data(ticker)
        if weekly_df is None:
            state.weekly_trend = 'unknown'
            state.is_aligned = True  # 无周线数据时优雅降级
            return state
        
        # 计算周线MA斜率
        state.weekly_ma20, state.weekly_ma20_slope, state.weekly_trend = \
            self._calculate_weekly_ma_slope(weekly_df)
        
        # 检查一致性
        state.is_aligned, state.rejection_reason = \
            self._check_alignment(state.daily_trend, state.weekly_trend)
        
        return state
    
    def filter(self, data: Dict[str, pd.DataFrame]) -> Tuple[Dict[str, pd.DataFrame], Dict[str, str]]:
        """
        过滤日/周趋势不一致的股票
        
        Args:
            data: {ticker: daily_dataframe}
        
        Returns:
            tuple: (通过的股票数据, 未通过的股票及原因)
        """
        if not self.enabled:
            self.logger.info("周趋势过滤器已禁用，跳过")
            return data, {}
        
        passed = {}
        rejected = {}
        stats = {'up_up': 0, 'conflict': 0, 'unknown': 0, 'sideways': 0}
        
        for ticker, daily_df in data.items():
            try:
                state = self.analyze_stock(ticker, daily_df)
                
                if state.is_aligned:
                    passed[ticker] = daily_df
                    # 统计
                    if state.weekly_trend == 'unknown':
                        stats['unknown'] += 1
                    elif state.daily_trend == state.weekly_trend:
                        stats['up_up'] += 1
                    else:
                        stats['sideways'] += 1
                else:
                    rejected[ticker] = state.rejection_reason or "日/周趋势不一致"
                    stats['conflict'] += 1
                    self.logger.debug(
                        f"{ticker}: 日线={state.daily_trend}, 周线={state.weekly_trend}, "
                        f"周MA20斜率={state.weekly_ma20_slope:.4f if state.weekly_ma20_slope else 'N/A'}"
                    )
                    
            except Exception as e:
                # 出错时优雅降级，允许通过
                passed[ticker] = daily_df
                self.logger.warning(f"分析 {ticker} 周趋势时出错: {e}，允许通过")
        
        self.logger.info(
            f"周趋势过滤: 通过 {len(passed)}/{len(data)}, 拒绝 {len(rejected)} | "
            f"趋势一致={stats['up_up']}, 冲突={stats['conflict']}, "
            f"横盘={stats['sideways']}, 数据缺失={stats['unknown']}"
        )
        
        return passed, rejected

