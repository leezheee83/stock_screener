"""
Data Fetcher - 数据采集模块 (多数据源版本)
支持 yfinance, Alpha Vantage, Polygon.io 等多个数据源
保持与旧版本的接口兼容性
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd

from .data_fetcher_multi import MultiSourceDataFetcher
from .utils import get_sp500_tickers, get_nasdaq100_tickers


class DataFetcher:
    """
    数据采集器 - 向后兼容的多数据源版本
    
    自动从配置中读取数据源设置，支持：
    - yfinance (Yahoo Finance) - 免费但限流严格
    - alphavantage (Alpha Vantage) - 需要API key
    - polygon (Polygon.io) - 需要API key
    """
    
    def __init__(self, history_days: int = 180, max_workers: int = 1, 
                 request_delay: float = 15.0, max_retries: int = 3,
                 source_type: str = 'yfinance', api_key: Optional[str] = None):
        """
        初始化数据采集器
        
        Args:
            history_days: 历史数据天数
            max_workers: 并发下载线程数（建议1，避免被限流）
            request_delay: 每次请求间延迟秒数
            max_retries: 失败重试次数
            source_type: 数据源类型 ('yfinance', 'alphavantage', 'polygon')
            api_key: API密钥（alphavantage和polygon需要）
        """
        self.logger = logging.getLogger(__name__)
        
        # 初始化多数据源采集器
        try:
            self.fetcher = MultiSourceDataFetcher(
                source_type=source_type,
                api_key=api_key,
                history_days=history_days,
                max_workers=max_workers,
                request_delay=request_delay,
                max_retries=max_retries
            )
            self.logger.info(f"数据采集器初始化完成 - 数据源: {source_type}, 延迟: {request_delay}秒")
        except Exception as e:
            self.logger.error(f"初始化数据采集器失败: {e}")
            raise
        
        # 保持与旧版本的兼容性
        self.history_days = history_days
        self.max_workers = max_workers
        self.request_delay = request_delay
        self.max_retries = max_retries
    
    def get_stock_list(self, universe: str = 'nasdaq100', custom_file: str = None) -> List[str]:
        """
        获取股票列表
        
        Args:
            universe: 股票池类型 (sp500, nasdaq100, custom)
            custom_file: 自定义股票列表文件路径
        
        Returns:
            List[str]: 股票代码列表
        """
        return self.fetcher.get_stock_list(universe, custom_file)
    
    def fetch_single_stock(self, ticker: str, period: str = 'daily', 
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None,
                          retry_count: int = 0) -> Optional[pd.DataFrame]:
        """
        获取单个股票的数据
        
        Args:
            ticker: 股票代码
            period: 时间周期 (daily, weekly, monthly)
            start_date: 开始日期
            end_date: 结束日期
            retry_count: 当前重试次数（保留以兼容旧代码）
        
        Returns:
            pd.DataFrame: 包含OHLCV数据的DataFrame，失败返回None
        """
        return self.fetcher.fetch_single_stock(ticker, period, start_date, end_date)
    
    def fetch_multiple_stocks(self, tickers: List[str], period: str = 'daily',
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None,
                             batch_size: int = 10) -> Dict[str, pd.DataFrame]:
        """
        分批获取多个股票的数据
        
        Args:
            tickers: 股票代码列表
            period: 时间周期
            start_date: 开始日期
            end_date: 结束日期
            batch_size: 每批处理的股票数量
        
        Returns:
            Dict[str, pd.DataFrame]: 股票代码到DataFrame的映射
        """
        return self.fetcher.fetch_multiple_stocks(tickers, period, start_date, end_date, batch_size)
    
    def fetch_all_timeframes(self, tickers: List[str]) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        获取所有时间周期的数据
        
        Args:
            tickers: 股票代码列表
        
        Returns:
            Dict: 嵌套字典 {timeframe: {ticker: dataframe}}
        """
        return self.fetcher.fetch_all_timeframes(tickers)
    
    def update_incremental(self, ticker: str, period: str, 
                          last_date: datetime) -> Optional[pd.DataFrame]:
        """
        增量更新数据
        
        Args:
            ticker: 股票代码
            period: 时间周期
            last_date: 最后一次数据的日期
        
        Returns:
            pd.DataFrame: 新数据，如果没有新数据则返回None
        """
        return self.fetcher.update_incremental(ticker, period, last_date)
