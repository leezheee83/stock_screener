#!/usr/bin/env python3
"""
股票数据分析示例
演示如何读取和分析CSV数据
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
from src.indicators import TechnicalIndicators


def analyze_stock(ticker: str, period: str = 'daily'):
    """
    分析单个股票
    
    Args:
        ticker: 股票代码，如 'META', 'AAPL'
        period: 周期 (daily, weekly, monthly)
    """
    # 读取数据
    file_path = f'data/{period}/{ticker}.csv'
    
    if not os.path.exists(file_path):
        print(f"错误: 找不到文件 {file_path}")
        return
    
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    
    print("=" * 70)
    print(f"股票分析: {ticker} ({period})")
    print("=" * 70)
    
    # 基本信息
    print(f"\n📊 数据概况:")
    print(f"   数据范围: {df['date'].min().strftime('%Y-%m-%d')} 至 {df['date'].max().strftime('%Y-%m-%d')}")
    print(f"   数据条数: {len(df)} 条")
    
    # 最新数据
    latest = df.iloc[-1]
    print(f"\n💰 最新价格 ({latest['date'].strftime('%Y-%m-%d')}):")
    print(f"   开盘: ${latest['open']:.2f}")
    print(f"   收盘: ${latest['close']:.2f}")
    print(f"   最高: ${latest['high']:.2f}")
    print(f"   最低: ${latest['low']:.2f}")
    print(f"   成交量: {latest['volume']:,}")
    
    # 计算技术指标
    indicators = TechnicalIndicators()
    df = indicators.add_all_indicators(df)
    
    latest = df.iloc[-1]  # 更新最新数据（包含指标）
    
    # 价格分析
    print(f"\n📈 价格分析:")
    if 'price_change_1d' in df.columns:
        change_1d = latest['price_change_1d']
        print(f"   日涨跌: {change_1d:+.2f}%")
    
    if 'price_change_5d' in df.columns:
        change_5d = latest['price_change_5d']
        print(f"   5日涨跌: {change_5d:+.2f}%")
    
    # 均线分析
    print(f"\n📉 均线分析:")
    for period in [5, 10, 20, 50, 200]:
        col_name = f'sma_{period}'
        if col_name in df.columns and not pd.isna(latest[col_name]):
            ma_value = latest[col_name]
            distance = ((latest['close'] - ma_value) / ma_value) * 100
            status = "上方" if distance > 0 else "下方"
            print(f"   MA{period:3d}: ${ma_value:7.2f} (价格在均线{status} {abs(distance):.2f}%)")
    
    # 技术指标
    print(f"\n🎯 技术指标:")
    
    if 'rsi' in df.columns and not pd.isna(latest['rsi']):
        rsi = latest['rsi']
        rsi_status = "超买" if rsi > 70 else "超卖" if rsi < 30 else "中性"
        print(f"   RSI(14): {rsi:.2f} ({rsi_status})")
    
    if 'macd' in df.columns and not pd.isna(latest['macd']):
        macd = latest['macd']
        signal = latest['macd_signal']
        hist = latest['macd_hist']
        macd_status = "多头" if hist > 0 else "空头"
        print(f"   MACD: {macd:.2f}, 信号线: {signal:.2f}, 柱状: {hist:.2f} ({macd_status})")
    
    if 'bb_upper' in df.columns:
        bb_upper = latest['bb_upper']
        bb_middle = latest['bb_middle']
        bb_lower = latest['bb_lower']
        price = latest['close']
        
        if price > bb_upper:
            bb_status = "突破上轨"
        elif price < bb_lower:
            bb_status = "跌破下轨"
        else:
            bb_status = "在轨道内"
        
        print(f"   布林带: 上轨${bb_upper:.2f}, 中轨${bb_middle:.2f}, 下轨${bb_lower:.2f} ({bb_status})")
    
    # 成交量分析
    print(f"\n📊 成交量分析:")
    if 'volume_ma' in df.columns and not pd.isna(latest['volume_ma']):
        vol_ma = latest['volume_ma']
        vol_ratio = latest['volume'] / vol_ma
        vol_status = "放大" if vol_ratio > 1.5 else "萎缩" if vol_ratio < 0.7 else "正常"
        print(f"   当前成交量: {latest['volume']:,}")
        print(f"   平均成交量: {vol_ma:,.0f}")
        print(f"   成交量比率: {vol_ratio:.2f}x ({vol_status})")
    
    # 趋势判断
    print(f"\n🔮 趋势判断:")
    
    # 均线排列
    if all(f'sma_{p}' in df.columns for p in [5, 10, 20, 50]):
        ma5 = latest['sma_5']
        ma10 = latest['sma_10']
        ma20 = latest['sma_20']
        ma50 = latest['sma_50']
        
        if all([not pd.isna(x) for x in [ma5, ma10, ma20, ma50]]):
            if ma5 > ma10 > ma20 > ma50:
                trend = "强势多头排列 🚀"
            elif ma5 < ma10 < ma20 < ma50:
                trend = "弱势空头排列 📉"
            elif latest['close'] > ma20:
                trend = "多头趋势 📈"
            elif latest['close'] < ma20:
                trend = "空头趋势 📉"
            else:
                trend = "盘整中 ↔️"
            
            print(f"   趋势: {trend}")
    
    # 支撑阻力
    recent_20 = df.tail(20)
    support = recent_20['low'].min()
    resistance = recent_20['high'].max()
    print(f"   近期支撑位: ${support:.2f}")
    print(f"   近期阻力位: ${resistance:.2f}")
    
    # 波动率
    if 'atr' in df.columns and not pd.isna(latest['atr']):
        atr = latest['atr']
        atr_pct = (atr / latest['close']) * 100
        volatility = "高" if atr_pct > 3 else "低" if atr_pct < 1 else "中等"
        print(f"   ATR: ${atr:.2f} ({atr_pct:.2f}%, 波动率{volatility})")
    
    print("\n" + "=" * 70)
    
    return df


def compare_stocks(tickers: list, period: str = 'daily'):
    """
    对比多只股票
    
    Args:
        tickers: 股票代码列表
        period: 周期
    """
    print("=" * 70)
    print(f"股票对比分析 ({period})")
    print("=" * 70)
    
    results = []
    
    for ticker in tickers:
        file_path = f'data/{period}/{ticker}.csv'
        if not os.path.exists(file_path):
            continue
        
        df = pd.read_csv(file_path)
        df['date'] = pd.to_datetime(df['date'])
        
        indicators = TechnicalIndicators()
        df = indicators.add_all_indicators(df)
        
        latest = df.iloc[-1]
        
        results.append({
            'ticker': ticker,
            'price': latest['close'],
            'change_1d': latest.get('price_change_1d', 0),
            'volume_ratio': latest.get('volume_ratio', 0),
            'rsi': latest.get('rsi', 0)
        })
    
    # 创建对比表
    df_compare = pd.DataFrame(results)
    
    print(f"\n{'股票':<8} {'价格':>10} {'日涨跌%':>10} {'成交量比':>10} {'RSI':>8}")
    print("-" * 70)
    
    for _, row in df_compare.iterrows():
        print(f"{row['ticker']:<8} ${row['price']:>9.2f} {row['change_1d']:>9.2f}% "
              f"{row['volume_ratio']:>9.2f}x {row['rsi']:>7.1f}")
    
    print("\n" + "=" * 70)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='股票数据分析工具')
    parser.add_argument('ticker', nargs='+', help='股票代码，如 META AAPL GOOGL')
    parser.add_argument('--period', '-p', default='daily', 
                       choices=['daily', 'weekly', 'monthly'],
                       help='时间周期')
    parser.add_argument('--compare', '-c', action='store_true',
                       help='对比模式')
    
    args = parser.parse_args()
    
    if args.compare and len(args.ticker) > 1:
        # 对比多只股票
        compare_stocks(args.ticker, args.period)
    else:
        # 分析单只股票
        for ticker in args.ticker:
            analyze_stock(ticker, args.period)
            if len(args.ticker) > 1:
                print("\n")

