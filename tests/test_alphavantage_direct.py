#!/usr/bin/env python3
"""
测试 AlphaVantage 数据获取的详细过程
"""

import sys
import os

# 添加父目录到路径以便导入src模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from src.data_fetcher_multi import AlphaVantageSource

# 测试
api_key = "JCYHE2IJVOIWUA52"
ticker = "AAPL"

print("="*60)
print("测试 Alpha Vantage 数据获取")
print("="*60)

# 创建数据源
source = AlphaVantageSource(api_key=api_key, request_delay=12.0)

# 设置日期范围 - 使用30天前到今天
start_date = datetime.now() - timedelta(days=30)
end_date = datetime.now()

print(f"\n股票: {ticker}")
print(f"日期范围: {start_date.date()} 到 {end_date.date()}")
print(f"间隔: 1d (daily)")

print("\n开始获取数据...")
df = source.fetch_stock_data(ticker, start_date, end_date, '1d')

if df is not None:
    print(f"\n✅ 成功获取数据!")
    print(f"数据形状: {df.shape}")
    print(f"列名: {list(df.columns)}")
    print(f"\n前5行:")
    print(df.head())
    print(f"\n最后5行:")
    print(df.tail())
else:
    print("\n❌ 获取数据失败，返回None")
    print("请查看上面的日志信息")
