"""
TrendFilter - 趋势硬门槛过滤器
过滤不符合趋势门槛的股票
"""

import logging
from typing import Dict, Tuple
import pandas as pd

from .base_filter import BaseFilter


class TrendFilter(BaseFilter):
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
        super().__init__(config)
        self.min_20d_return = config.get('min_20d_return', 0.0)
        self.require_above_ma50 = config.get('require_above_ma50', True)
        self.require_ma20_uptrend = config.get('require_ma20_uptrend', True)
    
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

