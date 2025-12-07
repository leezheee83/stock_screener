"""
DataQualityFilter - 数据质量过滤器
过滤数据质量不足的股票
"""

import logging
from typing import Dict, Tuple
import pandas as pd

from .base_filter import BaseFilter


class DataQualityFilter(BaseFilter):
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
        super().__init__(config)
        self.min_data_points = config.get('min_data_points', 100)
        self.required_columns = config.get('required_columns', ['close', 'volume', 'high', 'low'])
    
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

