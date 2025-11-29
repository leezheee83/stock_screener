"""
Data Storage - 数据存储模块
管理CSV格式的K线数据存储
"""

import os
import logging
from datetime import datetime
from typing import Dict, Optional, List
import pandas as pd
from pathlib import Path


class DataStorage:
    """数据存储管理器"""
    
    def __init__(self, base_dir: str = 'data'):
        """
        初始化数据存储管理器
        
        Args:
            base_dir: 数据存储根目录
        """
        self.base_dir = Path(base_dir)
        self.logger = logging.getLogger(__name__)
        
        # 确保目录存在
        self.daily_dir = self.base_dir / 'daily'
        self.weekly_dir = self.base_dir / 'weekly'
        self.monthly_dir = self.base_dir / 'monthly'
        
        for directory in [self.daily_dir, self.weekly_dir, self.monthly_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_directory(self, period: str) -> Path:
        """
        获取指定周期的存储目录
        
        Args:
            period: 时间周期 (daily, weekly, monthly)
        
        Returns:
            Path: 目录路径
        """
        period_map = {
            'daily': self.daily_dir,
            'weekly': self.weekly_dir,
            'monthly': self.monthly_dir
        }
        return period_map.get(period, self.daily_dir)
    
    def save_stock_data(self, ticker: str, df: pd.DataFrame, period: str = 'daily'):
        """
        保存单个股票的数据
        
        Args:
            ticker: 股票代码
            df: 数据DataFrame
            period: 时间周期
        """
        if df is None or df.empty:
            self.logger.warning(f"股票 {ticker} 没有数据可保存")
            return
        
        try:
            directory = self.get_directory(period)
            file_path = directory / f"{ticker}.csv"
            
            # 保存到CSV
            df.to_csv(file_path, index=False)
            self.logger.debug(f"已保存 {ticker} 的 {period} 数据到 {file_path}")
            
        except Exception as e:
            self.logger.error(f"保存 {ticker} 数据失败: {e}")
    
    def save_multiple_stocks(self, data_dict: Dict[str, pd.DataFrame], period: str = 'daily'):
        """
        批量保存多个股票的数据
        
        Args:
            data_dict: 股票代码到DataFrame的映射
            period: 时间周期
        """
        self.logger.info(f"开始保存 {len(data_dict)} 只股票的 {period} 数据")
        
        success_count = 0
        for ticker, df in data_dict.items():
            self.save_stock_data(ticker, df, period)
            success_count += 1
        
        self.logger.info(f"成功保存 {success_count} 只股票的数据")
    
    def load_stock_data(self, ticker: str, period: str = 'daily') -> Optional[pd.DataFrame]:
        """
        加载单个股票的数据
        
        Args:
            ticker: 股票代码
            period: 时间周期
        
        Returns:
            pd.DataFrame: 数据DataFrame，如果不存在返回None
        """
        try:
            directory = self.get_directory(period)
            file_path = directory / f"{ticker}.csv"
            
            if not file_path.exists():
                self.logger.debug(f"文件不存在: {file_path}")
                return None
            
            df = pd.read_csv(file_path)
            
            # 确保日期列为datetime类型
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
            
            self.logger.debug(f"已加载 {ticker} 的 {period} 数据，共 {len(df)} 条")
            return df
            
        except Exception as e:
            self.logger.error(f"加载 {ticker} 数据失败: {e}")
            return None
    
    def load_multiple_stocks(self, tickers: List[str], period: str = 'daily') -> Dict[str, pd.DataFrame]:
        """
        批量加载多个股票的数据
        
        Args:
            tickers: 股票代码列表
            period: 时间周期
        
        Returns:
            Dict[str, pd.DataFrame]: 股票代码到DataFrame的映射
        """
        self.logger.info(f"开始加载 {len(tickers)} 只股票的 {period} 数据")
        
        results = {}
        for ticker in tickers:
            df = self.load_stock_data(ticker, period)
            if df is not None:
                results[ticker] = df
        
        self.logger.info(f"成功加载 {len(results)} 只股票的数据")
        return results
    
    def get_latest_date(self, ticker: str, period: str = 'daily') -> Optional[datetime]:
        """
        获取指定股票最新的数据日期
        
        Args:
            ticker: 股票代码
            period: 时间周期
        
        Returns:
            datetime: 最新日期，如果没有数据返回None
        """
        df = self.load_stock_data(ticker, period)
        if df is None or df.empty:
            return None
        
        if 'date' in df.columns:
            latest_date = pd.to_datetime(df['date']).max()
            return latest_date.to_pydatetime()
        
        return None
    
    def append_stock_data(self, ticker: str, new_df: pd.DataFrame, period: str = 'daily'):
        """
        追加新数据到现有数据
        
        Args:
            ticker: 股票代码
            new_df: 新数据DataFrame
            period: 时间周期
        """
        if new_df is None or new_df.empty:
            return
        
        try:
            # 加载现有数据
            existing_df = self.load_stock_data(ticker, period)
            
            if existing_df is None or existing_df.empty:
                # 如果没有现有数据，直接保存新数据
                self.save_stock_data(ticker, new_df, period)
            else:
                # 合并数据并去重
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                
                # 根据日期去重，保留最新的
                if 'date' in combined_df.columns:
                    combined_df = combined_df.drop_duplicates(subset=['date'], keep='last')
                    combined_df = combined_df.sort_values('date')
                
                self.save_stock_data(ticker, combined_df, period)
                self.logger.info(f"已追加 {ticker} 的 {len(new_df)} 条新数据")
                
        except Exception as e:
            self.logger.error(f"追加 {ticker} 数据失败: {e}")
    
    def list_available_stocks(self, period: str = 'daily') -> List[str]:
        """
        列出指定周期下所有可用的股票
        
        Args:
            period: 时间周期
        
        Returns:
            List[str]: 股票代码列表
        """
        directory = self.get_directory(period)
        csv_files = directory.glob('*.csv')
        tickers = [f.stem for f in csv_files]
        return sorted(tickers)
    
    def get_storage_info(self) -> Dict[str, int]:
        """
        获取存储统计信息
        
        Returns:
            Dict: 各周期的股票数量
        """
        info = {}
        for period in ['daily', 'weekly', 'monthly']:
            stocks = self.list_available_stocks(period)
            info[period] = len(stocks)
        
        return info
    
    def clean_old_data(self, ticker: str, period: str = 'daily', keep_days: int = 365):
        """
        清理过旧的数据（可选功能）
        
        Args:
            ticker: 股票代码
            period: 时间周期
            keep_days: 保留的天数
        """
        df = self.load_stock_data(ticker, period)
        if df is None or df.empty:
            return
        
        try:
            if 'date' in df.columns:
                cutoff_date = datetime.now() - pd.Timedelta(days=keep_days)
                df['date'] = pd.to_datetime(df['date'])
                df_filtered = df[df['date'] >= cutoff_date]
                
                if len(df_filtered) < len(df):
                    self.save_stock_data(ticker, df_filtered, period)
                    removed_count = len(df) - len(df_filtered)
                    self.logger.info(f"已清理 {ticker} 的 {removed_count} 条旧数据")
                    
        except Exception as e:
            self.logger.error(f"清理 {ticker} 旧数据失败: {e}")

