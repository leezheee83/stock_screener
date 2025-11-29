"""
Custom Strategies - 自定义策略
用户可以在此文件中添加自己的选股策略
"""

from typing import List, Dict
import pandas as pd

from .base_strategy import BaseStrategy


class CustomStrategy(BaseStrategy):
    """
    自定义策略模板
    
    使用方法:
    1. 继承BaseStrategy类
    2. 实现scan方法
    3. 在配置文件中启用该策略
    
    示例：
    class MyStrategy(BaseStrategy):
        def __init__(self, config: Dict = None):
            super().__init__("MyStrategy", config)
        
        def scan(self, data: Dict[str, pd.DataFrame]) -> List[Dict]:
            results = []
            # 实现您的筛选逻辑
            return results
    """
    
    def __init__(self, config: Dict = None):
        super().__init__("Custom", config)
    
    def scan(self, data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """
        自定义筛选逻辑
        
        Args:
            data: 股票数据字典 {ticker: dataframe}
        
        Returns:
            List[Dict]: 符合条件的股票列表
        """
        results = []
        
        # TODO: 在此实现您的策略逻辑
        # 示例：
        # for ticker, df in data.items():
        #     latest = self.get_latest_row(df)
        #     if latest is not None:
        #         # 您的筛选条件
        #         if latest['close'] > latest['sma_20']:
        #             results.append({
        #                 'ticker': ticker,
        #                 'signal': '自定义信号',
        #                 'price': latest['close'],
        #                 'details': {}
        #             })
        
        return results


# 您可以在下方添加更多自定义策略类
# 例如：
#
# class MomentumStrategy(BaseStrategy):
#     """动量策略"""
#     def __init__(self, config: Dict = None):
#         super().__init__("Momentum", config)
#     
#     def scan(self, data: Dict[str, pd.DataFrame]) -> List[Dict]:
#         # 实现动量策略逻辑
#         pass

