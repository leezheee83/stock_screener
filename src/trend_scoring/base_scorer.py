"""
Base Trend Scorer - 趋势评分器基类
定义统一的评分器接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List
import pandas as pd
import logging


class BaseTrendScorer(ABC):
    """趋势评分器基类"""
    
    VERSION = "0.0.0"
    NAME = "base"
    DESCRIPTION = "基类"
    
    def __init__(self, config: dict):
        """
        初始化评分器
        
        Args:
            config: 评分器配置
        """
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.NAME}")
    
    @abstractmethod
    def score(self, df: pd.DataFrame) -> Dict:
        """
        计算单只股票的趋势得分
        
        Args:
            df: 包含技术指标的DataFrame
        
        Returns:
            {
                'total': float,           # 总分 0-100
                'components': dict,        # 各组成部分得分
                'pass_threshold': bool,    # 是否通过最低门槛
                'details': dict           # 详细信息
            }
        """
        pass
    
    @abstractmethod
    def get_required_indicators(self) -> List[str]:
        """
        返回需要的技术指标列表
        
        Returns:
            List[str]: 指标名称列表
        """
        pass
    
    def get_metadata(self) -> Dict:
        """
        返回评分器元数据
        
        Returns:
            Dict: 元数据信息
        """
        return {
            'version': self.VERSION,
            'name': self.NAME,
            'description': self.DESCRIPTION,
            'config': self.config
        }

