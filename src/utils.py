"""
Utility functions - 工具函数模块
"""

import logging
from datetime import datetime, timedelta
from typing import List
import pandas as pd


def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        log_file: 日志文件路径
        level: 日志级别
    
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(console_handler)
    
    return logger


def get_custom_tickers(file_path: str = 'config/custom_tickers.txt') -> List[str]:
    """
    从文件读取自定义股票列表
    
    Args:
        file_path: 股票列表文件路径
    
    Returns:
        List[str]: 股票代码列表
    """
    import os
    
    if not os.path.exists(file_path):
        logging.warning(f"自定义股票列表文件不存在: {file_path}")
        return []
    
    tickers = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释
                if line and not line.startswith('#'):
                    tickers.append(line.upper())
        
        logging.info(f"从 {file_path} 加载了 {len(tickers)} 只股票")
        return tickers
    except Exception as e:
        logging.error(f"读取自定义股票列表失败: {e}")
        return []


def get_sp500_tickers() -> List[str]:
    """
    获取S&P 500成分股列表
    
    Returns:
        List[str]: 股票代码列表
    """
    try:
        # 从Wikipedia获取S&P 500列表，添加headers避免403
        import requests
        from io import StringIO
        
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        tables = pd.read_html(StringIO(response.text))
        df = tables[0]
        tickers = df['Symbol'].tolist()
        # 清理股票代码（处理特殊字符）
        tickers = [ticker.replace('.', '-') for ticker in tickers]
        logging.info(f"成功获取 {len(tickers)} 只S&P 500股票")
        return tickers
    except Exception as e:
        logging.error(f"获取S&P 500列表失败: {e}")
        # 返回一些常见的股票作为备选
        logging.info("使用默认S&P 500股票列表")
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'WMT']


def get_nasdaq100_tickers() -> List[str]:
    """
    获取NASDAQ 100成分股列表
    
    Returns:
        List[str]: 股票代码列表
    """
    try:
        # 尝试从Wikipedia获取
        url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
        # 添加headers避免403错误
        import requests
        from io import StringIO
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        tables = pd.read_html(StringIO(response.text))
        
        # 尝试不同的表格索引
        for table in tables:
            if 'Ticker' in table.columns or 'Symbol' in table.columns:
                ticker_col = 'Ticker' if 'Ticker' in table.columns else 'Symbol'
                tickers = table[ticker_col].tolist()
                tickers = [str(ticker).replace('.', '-') for ticker in tickers if str(ticker) not in ['nan', 'None']]
                if len(tickers) > 50:  # 确保获取到足够多的股票
                    logging.info(f"成功获取 {len(tickers)} 只NASDAQ 100股票")
                    return tickers
        
        raise Exception("未找到有效的股票列表")
        
    except Exception as e:
        logging.error(f"获取NASDAQ 100列表失败: {e}")
        # 返回常见的NASDAQ 100成分股作为备选
        logging.info("使用默认NASDAQ 100股票列表")
        return [
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'TSLA', 'META', 'NVDA',
            'AVGO', 'COST', 'NFLX', 'AMD', 'PEP', 'ADBE', 'CSCO', 'CMCSA',
            'INTC', 'INTU', 'QCOM', 'TXN', 'AMGN', 'HON', 'SBUX', 'AMAT',
            'ISRG', 'BKNG', 'ADP', 'GILD', 'ADI', 'VRTX', 'MDLZ', 'REGN',
            'LRCX', 'PANW', 'MU', 'KLAC', 'SNPS', 'CDNS', 'MELI', 'PYPL'
        ]


def calculate_date_range(days: int) -> tuple:
    """
    计算日期范围
    
    Args:
        days: 历史天数
    
    Returns:
        tuple: (开始日期, 结束日期)
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """
    验证DataFrame是否包含必需的列
    
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
        logging.warning(f"缺少必需的列: {missing_columns}")
        return False
    
    return True

