"""
Filters - 硬过滤器模块
对股票进行硬性门槛过滤
"""

import pandas as pd
from typing import Dict, List, Tuple
import logging
import numpy as np


class LiquidityFilter:
    """流动性过滤器"""
    
    def __init__(self, config: dict):
        """
        初始化流动性过滤器
        
        Args:
            config: {
                'min_avg_dollar_volume': 1000000,  # 最小日均成交额（美元）
                'min_price': 5.0,                  # 最小价格
                'volume_period': 20                # 计算均量的周期
            }
        """
        self.min_avg_dollar_volume = config.get('min_avg_dollar_volume', 1000000)
        self.min_price = config.get('min_price', 5.0)
        self.volume_period = config.get('volume_period', 20)
        self.logger = logging.getLogger(__name__)
    
    def filter(self, data: Dict[str, pd.DataFrame]) -> Tuple[Dict[str, pd.DataFrame], Dict[str, str]]:
        """
        过滤流动性不足的股票
        
        Args:
            data: {ticker: dataframe}
        
        Returns:
            tuple: (通过的股票数据, 未通过的股票及原因)
        """
        passed = {}
        rejected = {}
        
        for ticker, df in data.items():
            try:
                if df is None or df.empty:
                    rejected[ticker] = "数据为空"
                    continue
                
                # 检查最新价格
                latest_price = df.iloc[-1]['close']
                if latest_price < self.min_price:
                    rejected[ticker] = f"价格过低 ${latest_price:.2f} < ${self.min_price}"
                    continue
                
                # 计算平均成交额（过去N天）
                recent_data = df.tail(self.volume_period)
                if len(recent_data) < self.volume_period:
                    rejected[ticker] = f"数据不足（需要{self.volume_period}天）"
                    continue
                
                avg_volume = recent_data['volume'].mean()
                avg_price = recent_data['close'].mean()
                avg_dollar_volume = avg_volume * avg_price
                
                if avg_dollar_volume < self.min_avg_dollar_volume:
                    rejected[ticker] = f"成交额过低 ${avg_dollar_volume:,.0f} < ${self.min_avg_dollar_volume:,.0f}"
                    continue
                
                # 通过过滤
                passed[ticker] = df
                
            except Exception as e:
                rejected[ticker] = f"处理错误: {str(e)}"
                self.logger.error(f"处理 {ticker} 时出错: {e}")
        
        self.logger.info(f"流动性过滤: 通过 {len(passed)}/{len(data)}, 拒绝 {len(rejected)}")
        return passed, rejected


class DataQualityFilter:
    """数据质量过滤器"""
    
    def __init__(self, config: dict):
        """
        初始化数据质量过滤器
        
        Args:
            config: {
                'min_data_points': 100,           # 最少数据点数
                'required_columns': [...]          # 必需的列
            }
        """
        self.min_data_points = config.get('min_data_points', 100)
        self.required_columns = config.get('required_columns', ['close', 'volume', 'high', 'low'])
        self.logger = logging.getLogger(__name__)
    
    def filter(self, data: Dict[str, pd.DataFrame]) -> Tuple[Dict[str, pd.DataFrame], Dict[str, str]]:
        """
        过滤数据质量不足的股票
        
        Args:
            data: {ticker: dataframe}
        
        Returns:
            tuple: (通过的股票数据, 未通过的股票及原因)
        """
        passed = {}
        rejected = {}
        
        for ticker, df in data.items():
            try:
                # 检查是否为空
                if df is None or df.empty:
                    rejected[ticker] = "数据为空"
                    continue
                
                # 检查数据点数量
                if len(df) < self.min_data_points:
                    rejected[ticker] = f"数据不足 {len(df)} < {self.min_data_points}"
                    continue
                
                # 检查必需的列
                missing_columns = set(self.required_columns) - set(df.columns)
                if missing_columns:
                    rejected[ticker] = f"缺少列: {missing_columns}"
                    continue
                
                # 检查关键列是否有过多NaN
                for col in self.required_columns:
                    nan_count = df[col].isna().sum()
                    nan_ratio = nan_count / len(df)
                    if nan_ratio > 0.1:  # 超过10%的NaN认为质量不合格
                        rejected[ticker] = f"列 {col} 有 {nan_ratio:.1%} 的NaN值"
                        break
                else:
                    # 通过所有检查
                    passed[ticker] = df
                    continue
                
            except Exception as e:
                rejected[ticker] = f"处理错误: {str(e)}"
                self.logger.error(f"处理 {ticker} 时出错: {e}")
        
        self.logger.info(f"数据质量过滤: 通过 {len(passed)}/{len(data)}, 拒绝 {len(rejected)}")
        return passed, rejected


class TrendFilter:
    """趋势硬门槛过滤器"""
    
    def __init__(self, config: dict):
        """
        初始化趋势过滤器
        
        Args:
            config: {
                'min_20d_return': 0.0,          # 20日最小涨幅（小数，0.05表示5%）
                'require_above_ma50': True,     # 是否要求在MA50上方
                'require_ma20_uptrend': True    # 是否要求MA20上升
            }
        """
        self.min_20d_return = config.get('min_20d_return', 0.0)
        self.require_above_ma50 = config.get('require_above_ma50', True)
        self.require_ma20_uptrend = config.get('require_ma20_uptrend', True)
        self.logger = logging.getLogger(__name__)
    
    def filter(self, data: Dict[str, pd.DataFrame]) -> Tuple[Dict[str, pd.DataFrame], Dict[str, str]]:
        """
        过滤不符合趋势门槛的股票
        
        Args:
            data: {ticker: dataframe}
        
        Returns:
            tuple: (通过的股票数据, 未通过的股票及原因)
        """
        passed = {}
        rejected = {}
        
        for ticker, df in data.items():
            try:
                if df is None or len(df) < 50:
                    rejected[ticker] = "数据不足（需要至少50天）"
                    continue
                
                latest = df.iloc[-1]
                current_price = latest['close']
                
                # 检查20日回报率
                if len(df) >= 20:
                    price_20d_ago = df.iloc[-20]['close']
                    return_20d = (current_price - price_20d_ago) / price_20d_ago
                    
                    if return_20d < self.min_20d_return:
                        rejected[ticker] = f"20日涨幅不足 {return_20d:.2%} < {self.min_20d_return:.2%}"
                        continue
                
                # 检查是否在MA50上方
                if self.require_above_ma50:
                    if 'sma_50' not in df.columns:
                        rejected[ticker] = "缺少MA50数据"
                        continue
                    
                    ma50 = latest['sma_50']
                    if pd.isna(ma50) or current_price <= ma50:
                        rejected[ticker] = f"价格在MA50下方 ${current_price:.2f} <= ${ma50:.2f}"
                        continue
                
                # 检查MA20是否上升
                if self.require_ma20_uptrend:
                    if 'sma_20' not in df.columns:
                        rejected[ticker] = "缺少MA20数据"
                        continue
                    
                    # 计算MA20的斜率（最近5天）
                    if len(df) >= 25:
                        recent_ma20 = df['sma_20'].tail(5)
                        if recent_ma20.isna().any():
                            rejected[ticker] = "MA20数据不完整"
                            continue
                        
                        # 简单斜率：最新值 vs 5天前值
                        ma20_now = recent_ma20.iloc[-1]
                        ma20_5d_ago = recent_ma20.iloc[0]
                        ma20_slope = (ma20_now - ma20_5d_ago) / ma20_5d_ago
                        
                        if ma20_slope <= 0:
                            rejected[ticker] = f"MA20下降趋势 斜率={ma20_slope:.4f}"
                            continue
                
                # 通过所有检查
                passed[ticker] = df
                
            except Exception as e:
                rejected[ticker] = f"处理错误: {str(e)}"
                self.logger.error(f"处理 {ticker} 时出错: {e}")
        
        self.logger.info(f"趋势过滤: 通过 {len(passed)}/{len(data)}, 拒绝 {len(rejected)}")
        return passed, rejected

