"""
Multi-Source Data Fetcher - 多数据源数据采集模块
支持 yfinance, Alpha Vantage, Polygon.io 等多个数据源
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from abc import ABC, abstractmethod

from .utils import get_sp500_tickers, get_nasdaq100_tickers, calculate_date_range


class DataSourceBase(ABC):
    """数据源基类"""
    
    def __init__(self, request_delay: float = 2.0, max_retries: int = 3):
        self.request_delay = request_delay
        self.max_retries = max_retries
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def fetch_stock_data(self, ticker: str, start_date: datetime, 
                        end_date: datetime, interval: str = '1d') -> Optional[pd.DataFrame]:
        """获取股票数据的抽象方法"""
        pass
    
    def _retry_fetch(self, ticker: str, start_date: datetime, 
                    end_date: datetime, interval: str, retry_count: int = 0) -> Optional[pd.DataFrame]:
        """带重试的获取数据"""
        try:
            df = self.fetch_stock_data(ticker, start_date, end_date, interval)
            return df
        except Exception as e:
            error_msg = str(e)
            
            # 如果是限流错误且还有重试次数
            if any(keyword in error_msg for keyword in ["Rate limited", "Too Many Requests", "429"]):
                if retry_count < self.max_retries:
                    wait_time = self.request_delay * (2 ** retry_count)
                    self.logger.warning(f"获取 {ticker} 触发限流，{wait_time:.0f}秒后重试 (第{retry_count+1}/{self.max_retries}次)")
                    time.sleep(wait_time)
                    return self._retry_fetch(ticker, start_date, end_date, interval, retry_count + 1)
            
            self.logger.error(f"获取 {ticker} 数据失败: {e}")
            return None


class YFinanceSource(DataSourceBase):
    """Yahoo Finance 数据源"""
    
    def __init__(self, request_delay: float = 10.0, max_retries: int = 3):
        """
        初始化 YFinance 数据源
        
        Args:
            request_delay: 请求延迟（秒）- 建议10-15秒避免限流
            max_retries: 最大重试次数
        """
        super().__init__(request_delay, max_retries)
        try:
            import yfinance as yf
            self.yf = yf
            self.logger.info(f"YFinance 数据源已初始化 (延迟: {request_delay}秒)")
        except ImportError:
            raise ImportError("请安装 yfinance: pip install yfinance")
    
    def fetch_stock_data(self, ticker: str, start_date: datetime, 
                        end_date: datetime, interval: str = '1d') -> Optional[pd.DataFrame]:
        """获取股票数据"""
        stock = self.yf.Ticker(ticker)
        df = stock.history(
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            interval=interval
        )
        
        if df.empty:
            self.logger.warning(f"股票 {ticker} 没有数据")
            return None
        
        # 标准化列名
        df.reset_index(inplace=True)
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]
        df['ticker'] = ticker
        
        return df


class AlphaVantageSource(DataSourceBase):
    """Alpha Vantage 数据源"""
    
    def __init__(self, api_key: str, request_delay: float = 12.0, max_retries: int = 3):
        """
        初始化 Alpha Vantage 数据源
        
        Args:
            api_key: API密钥（从 https://www.alphavantage.co/support/#api-key 获取）
            request_delay: 请求延迟（免费版：每分钟5次，建议12秒以上）
            max_retries: 最大重试次数
        """
        super().__init__(request_delay, max_retries)
        self.api_key = api_key
        try:
            import requests
            self.requests = requests
            self.logger.info(f"Alpha Vantage 数据源已初始化 (延迟: {request_delay}秒)")
        except ImportError:
            raise ImportError("请安装 requests: pip install requests")
    
    def fetch_stock_data(self, ticker: str, start_date: datetime, 
                        end_date: datetime, interval: str = '1d') -> Optional[pd.DataFrame]:
        """获取股票数据"""
        
        # Alpha Vantage 的时间序列函数
        if interval == '1d':
            function = 'TIME_SERIES_DAILY'
            outputsize = 'compact'  # 免费版只支持compact（最近100个交易日）
        elif interval == '1wk':
            function = 'TIME_SERIES_WEEKLY'
            outputsize = 'compact'  # 免费版限制
        elif interval == '1mo':
            function = 'TIME_SERIES_MONTHLY'
            outputsize = 'compact'  # 免费版限制
        else:
            self.logger.error(f"不支持的时间间隔: {interval}")
            return None
        
        url = f'https://www.alphavantage.co/query'
        params = {
            'function': function,
            'symbol': ticker,
            'outputsize': outputsize,
            'apikey': self.api_key,
            'datatype': 'json'
        }
        
        response = self.requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # 检查错误
        if 'Error Message' in data:
            self.logger.error(f"API错误: {data['Error Message']}")
            return None
        
        if 'Note' in data:
            # API调用频率超限
            raise Exception(f"Rate limited: {data['Note']}")
        
        if 'Information' in data:
            # API信息提示（通常是限流或其他提示）
            self.logger.warning(f"API提示: {data['Information']}")
            # 如果只有Information，说明没有数据，可能是限流
            if len(data.keys()) == 1:
                raise Exception(f"API限流或错误: {data['Information']}")
        
        # 解析数据
        time_series_key = [k for k in data.keys() if 'Time Series' in k]
        if not time_series_key:
            self.logger.warning(f"股票 {ticker} 没有数据，响应keys: {list(data.keys())}")
            return None
        
        time_series = data[time_series_key[0]]
        
        if not time_series:
            self.logger.warning(f"股票 {ticker} 时间序列为空")
            return None
        
        # 转换为DataFrame
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        # 标准化列名 - Alpha Vantage的列名格式是 "1. open", "2. high" 等
        column_mapping = {}
        for col in df.columns:
            col_lower = col.lower()
            if 'open' in col_lower:
                column_mapping[col] = 'open'
            elif 'high' in col_lower:
                column_mapping[col] = 'high'
            elif 'low' in col_lower:
                column_mapping[col] = 'low'
            elif 'close' in col_lower:
                column_mapping[col] = 'close'
            elif 'volume' in col_lower:
                column_mapping[col] = 'volume'
        
        df.rename(columns=column_mapping, inplace=True)
        df = df.astype(float)
        
        # 筛选日期范围
        df = df[(df.index >= start_date) & (df.index <= end_date)]
        
        if df.empty:
            return None
        
        # 重置索引并添加ticker列
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'date'}, inplace=True)
        df['ticker'] = ticker
        
        return df


class PolygonSource(DataSourceBase):
    """Polygon.io 数据源"""
    
    def __init__(self, api_key: str, request_delay: float = 12.0, max_retries: int = 3):
        """
        初始化 Polygon 数据源
        
        Args:
            api_key: API密钥（从 https://polygon.io/ 获取）
            request_delay: 请求延迟（免费版：每分钟5次，建议12秒以上）
            max_retries: 最大重试次数
        """
        super().__init__(request_delay, max_retries)
        self.api_key = api_key
        try:
            import requests
            self.requests = requests
            self.logger.info(f"Polygon 数据源已初始化 (延迟: {request_delay}秒)")
        except ImportError:
            raise ImportError("请安装 requests: pip install requests")
    
    def fetch_stock_data(self, ticker: str, start_date: datetime, 
                        end_date: datetime, interval: str = '1d') -> Optional[pd.DataFrame]:
        """获取股票数据"""
        
        # Polygon 的时间跨度参数
        timespan_map = {
            '1d': 'day',
            '1wk': 'week',
            '1mo': 'month'
        }
        timespan = timespan_map.get(interval, 'day')
        
        url = f'https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/{timespan}/{start_date.strftime("%Y-%m-%d")}/{end_date.strftime("%Y-%m-%d")}'
        params = {
            'adjusted': 'true',
            'sort': 'asc',
            'limit': 50000,
            'apiKey': self.api_key
        }
        
        response = self.requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # 检查错误
        if data.get('status') == 'ERROR':
            self.logger.error(f"API错误: {data.get('error', 'Unknown error')}")
            return None
        
        if data.get('status') == 'DELAYED':
            raise Exception("Rate limited: Too many requests")
        
        results = data.get('results', [])
        if not results:
            self.logger.warning(f"股票 {ticker} 没有数据")
            return None
        
        # 转换为DataFrame
        df = pd.DataFrame(results)
        
        # 标准化列名
        df.rename(columns={
            't': 'timestamp',
            'o': 'open',
            'h': 'high',
            'l': 'low',
            'c': 'close',
            'v': 'volume'
        }, inplace=True)
        
        # 转换时间戳
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.drop('timestamp', axis=1)
        
        # 添加ticker列
        df['ticker'] = ticker
        
        # 重新排列列
        df = df[['date', 'open', 'high', 'low', 'close', 'volume', 'ticker']]
        
        return df


class MultiSourceDataFetcher:
    """多数据源数据采集器"""
    
    def __init__(self, source_type: str = 'yfinance', api_key: Optional[str] = None,
                 history_days: int = 180, max_workers: int = 1, 
                 request_delay: float = 10.0, max_retries: int = 3):
        """
        初始化多数据源采集器
        
        Args:
            source_type: 数据源类型 ('yfinance', 'alphavantage', 'polygon')
            api_key: API密钥（alphavantage和polygon需要）
            history_days: 历史数据天数
            max_workers: 并发下载线程数（建议1）
            request_delay: 每次请求间延迟秒数
            max_retries: 失败重试次数
        """
        self.history_days = history_days
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)
        
        # 初始化数据源
        source_type = source_type.lower()
        if source_type == 'yfinance':
            self.data_source = YFinanceSource(request_delay, max_retries)
        elif source_type == 'alphavantage':
            if not api_key:
                raise ValueError("Alpha Vantage 需要 API key")
            self.data_source = AlphaVantageSource(api_key, request_delay, max_retries)
        elif source_type == 'polygon':
            if not api_key:
                raise ValueError("Polygon 需要 API key")
            self.data_source = PolygonSource(api_key, request_delay, max_retries)
        else:
            raise ValueError(f"不支持的数据源类型: {source_type}")
        
        self.logger.info(f"数据采集器初始化完成 - 数据源: {source_type}")
    
    def get_stock_list(self, universe: str = 'nasdaq100', custom_file: str = None) -> List[str]:
        """获取股票列表"""
        self.logger.info(f"获取股票列表: {universe}")
        
        if universe.lower() == 'sp500':
            return get_sp500_tickers()
        elif universe.lower() == 'nasdaq100':
            return get_nasdaq100_tickers()
        elif universe.lower() == 'custom':
            from .utils import get_custom_tickers
            tickers = get_custom_tickers(custom_file or 'config/custom_tickers.txt')
            if not tickers:
                self.logger.warning("自定义列表为空，使用默认列表")
                return get_sp500_tickers()
            return tickers
        else:
            self.logger.warning(f"未知的股票池类型: {universe}，使用默认列表")
            return get_sp500_tickers()
    
    def fetch_single_stock(self, ticker: str, period: str = 'daily', 
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> Optional[pd.DataFrame]:
        """获取单个股票的数据"""
        
        # 设置日期范围
        if start_date is None or end_date is None:
            start_date, end_date = calculate_date_range(self.history_days)
        
        # 根据周期设置interval
        interval_map = {
            'daily': '1d',
            'weekly': '1wk',
            'monthly': '1mo'
        }
        interval = interval_map.get(period, '1d')
        
        # 使用数据源获取数据
        df = self.data_source._retry_fetch(ticker, start_date, end_date, interval)
        
        if df is not None and not df.empty:
            self.logger.debug(f"成功获取 {ticker} 的 {period} 数据，共 {len(df)} 条")
        
        return df
    
    def fetch_multiple_stocks(self, tickers: List[str], period: str = 'daily',
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None,
                             batch_size: int = 10) -> Dict[str, pd.DataFrame]:
        """分批获取多个股票的数据"""
        self.logger.info(f"开始获取 {len(tickers)} 只股票的 {period} 数据（分批处理，每批{batch_size}只）")
        
        results = {}
        failed_tickers = []
        
        # 分批处理
        for batch_idx in range(0, len(tickers), batch_size):
            batch_tickers = tickers[batch_idx:batch_idx + batch_size]
            batch_num = batch_idx // batch_size + 1
            total_batches = (len(tickers) + batch_size - 1) // batch_size
            
            self.logger.info(f"处理第 {batch_num}/{total_batches} 批，共 {len(batch_tickers)} 只股票")
            
            # 串行处理（最安全）
            for ticker in batch_tickers:
                df = self.fetch_single_stock(ticker, period, start_date, end_date)
                if df is not None and not df.empty:
                    results[ticker] = df
                    self.logger.info(f"✓ {ticker} ({len(results)}/{len(tickers)})")
                else:
                    failed_tickers.append(ticker)
                    self.logger.warning(f"✗ {ticker} 失败")
                
                # 每次请求后延迟
                time.sleep(self.data_source.request_delay)
            
            # 批次之间增加更长的延迟
            if batch_idx + batch_size < len(tickers):
                batch_delay = self.data_source.request_delay * 2
                self.logger.info(f"等待 {batch_delay:.1f} 秒后处理下一批...")
                time.sleep(batch_delay)
        
        success_count = len(results)
        failed_count = len(failed_tickers)
        
        self.logger.info(
            f"数据获取完成: 成功 {success_count}/{len(tickers)}, 失败 {failed_count}"
        )
        
        if failed_tickers:
            self.logger.warning(f"失败的股票: {', '.join(failed_tickers[:10])}" + 
                              (f" ... (还有 {len(failed_tickers)-10} 只)" 
                               if len(failed_tickers) > 10 else ""))
        
        return results
    
    def fetch_all_timeframes(self, tickers: List[str]) -> Dict[str, Dict[str, pd.DataFrame]]:
        """获取所有时间周期的数据"""
        self.logger.info("开始获取多周期数据（日K、周K、月K）")
        
        all_data = {}
        
        for period in ['daily', 'weekly', 'monthly']:
            self.logger.info(f"正在获取 {period} 数据...")
            period_data = self.fetch_multiple_stocks(tickers, period)
            all_data[period] = period_data
            
            # 在不同周期之间增加延迟
            self.logger.info(f"{period} 数据获取完成，等待 {self.data_source.request_delay * 3:.1f} 秒后继续...")
            time.sleep(self.data_source.request_delay * 3)
        
        self.logger.info("所有周期数据获取完成")
        return all_data
    
    def update_incremental(self, ticker: str, period: str, 
                          last_date: datetime) -> Optional[pd.DataFrame]:
        """增量更新数据"""
        start_date = last_date + timedelta(days=1)
        end_date = datetime.now()
        
        if start_date >= end_date:
            self.logger.debug(f"{ticker} {period} 数据已是最新")
            return None
        
        return self.fetch_single_stock(ticker, period, start_date, end_date)
