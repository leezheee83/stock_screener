#!/usr/bin/env python3
"""
Alpha Vantage 调试脚本
用于诊断API连接和响应问题
"""

import requests
import json
from datetime import datetime, timedelta

# 使用你的API key
API_KEY = "JCYHE2IJVOIWUA52"
TICKER = "AAPL"

print("="*60)
print("Alpha Vantage API 调试")
print("="*60)

# 测试1: 检查API key是否有效
print("\n[测试1] 检查API连接和key有效性")
print(f"API Key: {API_KEY}")
print(f"测试股票: {TICKER}")

url = 'https://www.alphavantage.co/query'
params = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': TICKER,
    'outputsize': 'compact',  # 先用compact测试
    'apikey': API_KEY,
    'datatype': 'json'
}

print(f"\n请求URL: {url}")
print(f"请求参数: {params}")

try:
    print("\n发送请求...")
    response = requests.get(url, params=params, timeout=30)
    print(f"响应状态码: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ HTTP错误: {response.status_code}")
        print(f"响应内容: {response.text[:500]}")
        exit(1)
    
    data = response.json()
    
    # 打印原始响应（前面部分）
    print("\n原始响应结构:")
    print(json.dumps(data, indent=2)[:1000] + "...")
    
    # 检查错误信息
    if 'Error Message' in data:
        print(f"\n❌ API错误: {data['Error Message']}")
        exit(1)
    
    if 'Note' in data:
        print(f"\n⚠️  API限流: {data['Note']}")
        print("建议: 稍后再试或增加请求延迟")
        exit(1)
    
    if 'Information' in data:
        print(f"\n⚠️  API信息: {data['Information']}")
        exit(1)
    
    # 查找时间序列数据
    print("\n[测试2] 检查响应数据结构")
    print(f"响应keys: {list(data.keys())}")
    
    time_series_key = None
    for key in data.keys():
        if 'Time Series' in key:
            time_series_key = key
            print(f"✅ 找到时间序列key: {time_series_key}")
            break
    
    if not time_series_key:
        print("❌ 未找到时间序列数据")
        print("可用的keys:", list(data.keys()))
        exit(1)
    
    # 检查数据内容
    time_series = data[time_series_key]
    dates = list(time_series.keys())
    
    print(f"\n✅ 数据获取成功!")
    print(f"数据点数量: {len(dates)}")
    print(f"日期范围: {dates[-1]} 到 {dates[0]}")
    
    # 显示最新几条数据
    print("\n最新3条数据:")
    for i, date in enumerate(dates[:3]):
        print(f"  {date}: {time_series[date]}")
    
    # 测试3: 检查数据格式
    print("\n[测试3] 检查数据格式")
    latest_date = dates[0]
    latest_data = time_series[latest_date]
    print(f"数据字段: {list(latest_data.keys())}")
    
    # 检查是否有必需字段
    expected_fields = ['1. open', '2. high', '3. low', '4. close', '5. volume']
    missing_fields = [f for f in expected_fields if f not in latest_data]
    
    if missing_fields:
        print(f"⚠️  缺少字段: {missing_fields}")
    else:
        print("✅ 所有必需字段都存在")
    
    # 测试4: 模拟解析过程
    print("\n[测试4] 模拟数据解析")
    import pandas as pd
    
    df = pd.DataFrame.from_dict(time_series, orient='index')
    print(f"DataFrame形状: {df.shape}")
    print(f"列名: {list(df.columns)}")
    print(f"\n前3行:")
    print(df.head(3))
    
    # 测试日期过滤
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()
    
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df_filtered = df[(df.index >= start_date) & (df.index <= end_date)]
    
    print(f"\n日期过滤后 ({start_date.date()} 到 {end_date.date()}):")
    print(f"剩余数据点: {len(df_filtered)}")
    
    if len(df_filtered) == 0:
        print("⚠️  日期过滤后没有数据 - 这可能是问题所在!")
        print(f"数据日期范围: {df.index.min()} 到 {df.index.max()}")
        print(f"请求日期范围: {start_date.date()} 到 {end_date.date()}")
    else:
        print("✅ 日期过滤正常")
    
    print("\n" + "="*60)
    print("诊断完成!")
    print("="*60)

except requests.exceptions.Timeout:
    print("\n❌ 请求超时")
    print("建议: 检查网络连接")
except requests.exceptions.ConnectionError:
    print("\n❌ 连接错误")
    print("建议: 检查网络连接和防火墙设置")
except Exception as e:
    print(f"\n❌ 发生错误: {e}")
    import traceback
    traceback.print_exc()
