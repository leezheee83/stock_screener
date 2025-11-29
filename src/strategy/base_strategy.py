"""
Base Strategy - 策略基类
定义统一的策略接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import pandas as pd
import logging


class BaseStrategy(ABC):
    """
    策略基类
    所有策略都应继承此类并实现scan方法
    """
    
    def __init__(self, name: str, config: Optional[Dict] = None):
        """
        初始化策略
        
        Args:
            name: 策略名称
            config: 策略配置参数
        """
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    def scan(self, data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """
        执行股票筛选
        
        Args:
            data: 股票数据字典 {ticker: dataframe}
        
        Returns:
            List[Dict]: 符合条件的股票列表，每个字典包含：
                - ticker: 股票代码
                - signal: 信号类型
                - price: 当前价格
                - details: 详细信息（可选）
        """
        pass
    
    def get_latest_row(self, df: pd.DataFrame) -> Optional[pd.Series]:
        """
        获取最新的一行数据
        
        Args:
            df: 数据DataFrame
        
        Returns:
            pd.Series: 最新的一行，如果为空则返回None
        """
        if df is None or df.empty:
            return None
        return df.iloc[-1]
    
    def get_previous_row(self, df: pd.DataFrame, offset: int = 1) -> Optional[pd.Series]:
        """
        获取前几行的数据
        
        Args:
            df: 数据DataFrame
            offset: 偏移量（1表示前一行）
        
        Returns:
            pd.Series: 指定的一行，如果不存在则返回None
        """
        if df is None or len(df) < offset + 1:
            return None
        return df.iloc[-(offset + 1)]
    
    def validate_data(self, df: pd.DataFrame, required_columns: List[str]) -> bool:
        """
        验证数据是否包含必需的列
        
        Args:
            df: 要验证的DataFrame
            required_columns: 必需的列名列表
        
        Returns:
            bool: 是否有效
        """
        if df is None or df.empty:
            return False
        
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            self.logger.debug(f"缺少必需的列: {missing_columns}")
            return False
        
        return True
    
    def log_signal(self, ticker: str, signal_type: str, details: str = ""):
        """
        记录信号日志
        
        Args:
            ticker: 股票代码
            signal_type: 信号类型
            details: 详细信息
        """
        self.logger.info(f"[{self.name}] {ticker} - {signal_type} {details}")
    
    def get_config_value(self, key: str, default=None):
        """
        获取配置值
        
        Args:
            key: 配置键
            default: 默认值
        
        Returns:
            配置值或默认值
        """
        return self.config.get(key, default)

