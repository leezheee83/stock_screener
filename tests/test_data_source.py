#!/usr/bin/env python3
"""
数据源测试脚本
用于快速测试不同数据源的连接和数据质量
"""

import sys
import os

# 添加父目录到路径以便导入src模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from datetime import datetime, timedelta
from src.data_fetcher_multi import MultiSourceDataFetcher

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_data_source(source_type, api_key=None, test_tickers=['AAPL', 'MSFT', 'GOOGL']):
    """
    测试数据源
    
    Args:
        source_type: 数据源类型 ('yfinance', 'alphavantage', 'polygon')
        api_key: API密钥（如果需要）
        test_tickers: 测试的股票代码列表
    """
    print("\n" + "="*60)
    print(f"测试数据源: {source_type.upper()}")
    print("="*60)
    
    try:
        # 初始化数据采集器
        if source_type == 'yfinance':
            request_delay = 15.0
        else:
            request_delay = 12.0
        
        fetcher = MultiSourceDataFetcher(
            source_type=source_type,
            api_key=api_key,
            history_days=30,  # 只获取30天数据以加快测试
            max_workers=1,
            request_delay=request_delay,
            max_retries=3
        )
        
        print(f"✓ 数据采集器初始化成功")
        print(f"  - 请求延迟: {request_delay}秒")
        print(f"  - 测试股票: {', '.join(test_tickers)}")
        print()
        
        # 测试获取数据
        results = {}
        for ticker in test_tickers:
            print(f"正在获取 {ticker} 数据...", end=' ')
            
            start_time = datetime.now()
            df = fetcher.fetch_single_stock(ticker, period='daily')
            elapsed = (datetime.now() - start_time).total_seconds()
            
            if df is not None and not df.empty:
                results[ticker] = df
                print(f"✓ 成功 ({len(df)} 条记录, 耗时 {elapsed:.1f}秒)")
                
                # 显示最新数据
                latest = df.iloc[-1]
                print(f"  最新数据: 日期={latest['date']}, 收盘价=${latest['close']:.2f}")
            else:
                print(f"✗ 失败")
            
            print()
        
        # 统计
        success_count = len(results)
        total_count = len(test_tickers)
        
        print("-"*60)
        print(f"测试完成: {success_count}/{total_count} 成功")
        
        if success_count == total_count:
            print("✓ 所有测试通过，数据源可用")
            return True
        elif success_count > 0:
            print("⚠ 部分测试通过，数据源可能不稳定")
            return False
        else:
            print("✗ 所有测试失败，数据源不可用")
            return False
            
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='数据源测试工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 测试 Yahoo Finance
  python test_data_source.py --source yfinance
  
  # 测试 Alpha Vantage（需要API key）
  python test_data_source.py --source alphavantage --api-key YOUR_KEY
  
  # 测试 Polygon（需要API key）
  python test_data_source.py --source polygon --api-key YOUR_KEY
  
  # 测试指定股票
  python test_data_source.py --source yfinance --tickers AAPL TSLA NVDA
        """
    )
    
    parser.add_argument('--source', '-s', 
                       choices=['yfinance', 'alphavantage', 'polygon'],
                       default='yfinance',
                       help='数据源类型')
    parser.add_argument('--api-key', '-k',
                       type=str,
                       help='API密钥（alphavantage和polygon需要）')
    parser.add_argument('--tickers', '-t',
                       nargs='+',
                       default=['AAPL', 'MSFT', 'GOOGL'],
                       help='测试的股票代码列表')
    
    args = parser.parse_args()
    
    # 检查API key
    if args.source in ['alphavantage', 'polygon'] and not args.api_key:
        print(f"错误: {args.source} 需要提供 API key")
        print(f"使用 --api-key 参数提供")
        sys.exit(1)
    
    # 运行测试
    success = test_data_source(args.source, args.api_key, args.tickers)
    
    # 如果成功，提示如何配置
    if success:
        print("\n" + "="*60)
        print("配置建议")
        print("="*60)
        print(f"在 config/config.yaml 中添加以下配置:")
        print()
        print("data:")
        print("  source:")
        print(f"    type: {args.source}")
        if args.api_key:
            print(f"    api_key: \"{args.api_key}\"")
        else:
            print("    api_key: \"\"")
        
        if args.source == 'yfinance':
            print("    request_delay: 15.0")
        else:
            print("    request_delay: 12.0")
        
        print("    max_retries: 3")
        print("    max_workers: 1")
        print("    batch_size: 10")
        print()
        
        sys.exit(0)
    else:
        print("\n测试失败，请检查:")
        print("1. 网络连接是否正常")
        print("2. API key 是否正确（如果使用）")
        print("3. 股票代码是否有效")
        sys.exit(1)


if __name__ == '__main__':
    main()
