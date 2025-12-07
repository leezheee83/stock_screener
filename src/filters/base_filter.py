"""
BaseFilter - 过滤器基类
定义过滤器接口规范
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Tuple
import pandas as pd


class BaseFilter(ABC):
    """过滤器基类"""
    
    def __init__(self, config: dict):
        """
        初始化过滤器
        
        Args:
            config: 过滤器配置字典
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def filter(self, data: Dict[str, pd.DataFrame]) -> Tuple[Dict[str, pd.DataFrame], Dict[str, str]]:
        """
        执行过滤
        
        Args:
            data: {ticker: dataframe} 股票数据字典
        
        Returns:
            tuple: (通过的股票数据, 未通过的股票及原因)
        """
        pass
    
    @property
    def name(self) -> str:
        """过滤器名称"""
        return self.__class__.__name__

