"""
LiquidityFilter - 流动性过滤器
过滤流动性不足的股票
"""

import logging
from typing import Dict, Tuple
import pandas as pd

from .base_filter import BaseFilter


class LiquidityFilter(BaseFilter):
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
        super().__init__(config)
        self.min_avg_dollar_volume = config.get('min_avg_dollar_volume', 1000000)
        self.min_price = config.get('min_price', 5.0)
        self.volume_period = config.get('volume_period', 20)
    
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

