"""
Data Fetcher - 数据采集模块
使用yfinance获取美股K线数据
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from .utils import get_sp500_tickers, get_nasdaq100_tickers, calculate_date_range


class DataFetcher:
    """数据采集器"""
    
    def __init__(self, history_days: int = 180, max_workers: int = 1, request_delay: float = 2.0, max_retries: int = 3):
        """
        初始化数据采集器
        
        Args:
            history_days: 历史数据天数
            max_workers: 并发下载线程数（建议1，避免被限流）
            request_delay: 每次请求间延迟秒数（建议2-3秒）
            max_retries: 失败重试次数
        """
        self.history_days = history_days
        self.max_workers = max_workers
        self.request_delay = request_delay
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)
        
    def get_stock_list(self, universe: str = 'nasdaq100', custom_file: str = None) -> List[str]:
        """
        获取股票列表
        
        Args:
            universe: 股票池类型 (sp500, nasdaq100, custom)
            custom_file: 自定义股票列表文件路径
        
        Returns:
            List[str]: 股票代码列表
        """
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
                          end_date: Optional[datetime] = None,
                          retry_count: int = 0) -> Optional[pd.DataFrame]:
        """
        获取单个股票的数据（带重试机制）
        
        Args:
            ticker: 股票代码
            period: 时间周期 (daily, weekly, monthly)
            start_date: 开始日期
            end_date: 结束日期
            retry_count: 当前重试次数
        
        Returns:
            pd.DataFrame: 包含OHLCV数据的DataFrame，失败返回None
        """
        try:
            # 创建股票对象
            stock = yf.Ticker(ticker)
            
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
            
            # 下载数据
            df = stock.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval=interval
            )
            
            if df.empty:
                self.logger.warning(f"股票 {ticker} 没有数据")
                return None
            
            # 添加股票代码列
            df['Ticker'] = ticker
            
            # 重置索引，使日期成为列
            df.reset_index(inplace=True)
            
            # 标准化列名
            df.columns = [col.lower().replace(' ', '_') for col in df.columns]
            
            self.logger.debug(f"成功获取 {ticker} 的 {period} 数据，共 {len(df)} 条")
            return df
            
        except Exception as e:
            error_msg = str(e)
            
            # 如果是限流错误且还有重试次数
            if "Rate limited" in error_msg or "Too Many Requests" in error_msg:
                if retry_count < self.max_retries:
                    # 指数退避：等待时间随重试次数增加
                    wait_time = self.request_delay * (2 ** retry_count)
                    self.logger.warning(f"获取 {ticker} 触发限流，{wait_time:.0f}秒后重试 (第{retry_count+1}/{self.max_retries}次)")
                    time.sleep(wait_time)
                    return self.fetch_single_stock(ticker, period, start_date, end_date, retry_count + 1)
            
            self.logger.error(f"获取 {ticker} 数据失败: {e}")
            return None
    
    def fetch_multiple_stocks(self, tickers: List[str], period: str = 'daily',
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None,
                             batch_size: int = 10) -> Dict[str, pd.DataFrame]:
        """
        分批获取多个股票的数据（避免限流）
        
        Args:
            tickers: 股票代码列表
            period: 时间周期
            start_date: 开始日期
            end_date: 结束日期
            batch_size: 每批处理的股票数量
        
        Returns:
            Dict[str, pd.DataFrame]: 股票代码到DataFrame的映射
        """
        self.logger.info(f"开始获取 {len(tickers)} 只股票的 {period} 数据（分批处理，每批{batch_size}只）")
        
        results = {}
        failed_tickers = []
        
        # 分批处理
        for batch_idx in range(0, len(tickers), batch_size):
            batch_tickers = tickers[batch_idx:batch_idx + batch_size]
            batch_num = batch_idx // batch_size + 1
            total_batches = (len(tickers) + batch_size - 1) // batch_size
            
            self.logger.info(f"处理第 {batch_num}/{total_batches} 批，共 {len(batch_tickers)} 只股票")
            
            # 如果并发数为1，使用串行处理（最安全）
            if self.max_workers == 1:
                for ticker in batch_tickers:
                    df = self.fetch_single_stock(ticker, period, start_date, end_date)
                    if df is not None and not df.empty:
                        results[ticker] = df
                        self.logger.info(f"✓ {ticker} ({len(results)}/{len(tickers)})")
                    else:
                        failed_tickers.append(ticker)
                        self.logger.warning(f"✗ {ticker} 失败")
                    
                    # 每次请求后延迟
                    time.sleep(self.request_delay)
            else:
                # 使用线程池（谨慎使用）
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    future_to_ticker = {
                        executor.submit(
                            self.fetch_single_stock, ticker, period, start_date, end_date
                        ): ticker 
                        for ticker in batch_tickers
                    }
                    
                    for future in as_completed(future_to_ticker):
                        ticker = future_to_ticker[future]
                        try:
                            df = future.result()
                            if df is not None and not df.empty:
                                results[ticker] = df
                            else:
                                failed_tickers.append(ticker)
                        except Exception as e:
                            self.logger.error(f"处理 {ticker} 时出错: {e}")
                            failed_tickers.append(ticker)
                        
                        time.sleep(self.request_delay)
            
            # 批次之间增加更长的延迟
            if batch_idx + batch_size < len(tickers):
                batch_delay = self.request_delay * 5
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
        """
        获取所有时间周期的数据
        
        Args:
            tickers: 股票代码列表
        
        Returns:
            Dict: 嵌套字典 {timeframe: {ticker: dataframe}}
        """
        self.logger.info("开始获取多周期数据（日K、周K、月K）")
        
        all_data = {}
        
        for period in ['daily', 'weekly', 'monthly']:
            self.logger.info(f"正在获取 {period} 数据...")
            period_data = self.fetch_multiple_stocks(tickers, period)
            all_data[period] = period_data
            
            # 在不同周期之间增加延迟，避免限流
            self.logger.info(f"{period} 数据获取完成，等待 {self.request_delay * 3:.1f} 秒后继续...")
            time.sleep(self.request_delay * 3)
        
        self.logger.info("所有周期数据获取完成")
        return all_data
    
    def update_incremental(self, ticker: str, period: str, 
                          last_date: datetime) -> Optional[pd.DataFrame]:
        """
        增量更新数据（仅获取自last_date以来的新数据）
        
        Args:
            ticker: 股票代码
            period: 时间周期
            last_date: 最后一次数据的日期
        
        Returns:
            pd.DataFrame: 新数据，如果没有新数据则返回None
        """
        # 从最后日期的下一天开始
        start_date = last_date + timedelta(days=1)
        end_date = datetime.now()
        
        # 如果没有新数据需要下载
        if start_date >= end_date:
            self.logger.debug(f"{ticker} {period} 数据已是最新")
            return None
        
        return self.fetch_single_stock(ticker, period, start_date, end_date)

