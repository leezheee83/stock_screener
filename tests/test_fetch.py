#!/usr/bin/env python3
"""
测试数据采集 - 只下载少量股票进行测试
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data_fetcher import DataFetcher
from src.data_storage import DataStorage
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_fetch():
    """测试下载少量股票"""
    
    # 创建采集器（保守配置）
    fetcher = DataFetcher(
        history_days=180,
        max_workers=1,      # 串行
        request_delay=3.0,  # 3秒延迟
        max_retries=2
    )
    
    # 只测试7只股票
    test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'META', 'AMZN']
    
    print("=" * 60)
    print(f"测试下载 {len(test_tickers)} 只股票的数据")
    print("配置: 串行下载，每次间隔3秒，失败重试2次")
    print("=" * 60)
    print()
    
    # 只下载日K数据
    data = fetcher.fetch_multiple_stocks(
        test_tickers,
        period='daily',
        batch_size=5  # 小批量
    )
    
    print()
    print("=" * 60)
    print(f"结果: 成功下载 {len(data)}/{len(test_tickers)} 只股票")
    print("=" * 60)
    
    if data:
        print("\n成功的股票:")
        for ticker, df in data.items():
            print(f"  ✓ {ticker}: {len(df)} 条数据")
        
        # 保存数据
        storage = DataStorage()
        storage.save_multiple_stocks(data, 'daily')
        print(f"\n数据已保存到 data/daily/")
    
    return len(data) == len(test_tickers)

if __name__ == '__main__':
    print("\n⚠️  注意: 如果刚才触发了限流，建议等待5-10分钟再运行\n")
    
    input("按Enter键开始测试...")
    
    success = test_fetch()
    
    if success:
        print("\n✅ 测试成功! 配置正常，可以开始全量下载")
        print("\n建议:")
        print("1. 如果需要下载全部股票，运行: python3 main.py --init")
        print("2. 全量下载约需要 2-3 小时（102只股票 × 3个周期 × 2秒/次）")
        print("3. 或者修改配置只下载部分股票")
    else:
        print("\n⚠️  部分股票下载失败")
        print("建议:")
        print("1. 等待10-15分钟后重试")
        print("2. 检查网络连接")
        print("3. 考虑使用VPN")

