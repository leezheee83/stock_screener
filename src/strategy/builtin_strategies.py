"""
Builtin Strategies - 内置策略
提供常用的选股策略示例
"""

from typing import List, Dict
import pandas as pd
import numpy as np

from .base_strategy import BaseStrategy


class MACrossoverStrategy(BaseStrategy):
    """
    均线交叉策略
    当短期均线向上突破长期均线时产生买入信号
    """
    
    def __init__(self, config: Dict = None):
        default_config = {
            'short_period': 20,
            'long_period': 50,
            'volume_confirm': True  # 是否需要成交量确认
        }
        if config:
            default_config.update(config)
        
        super().__init__("MA_Crossover", default_config)
    
    def scan(self, data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """
        扫描均线交叉信号
        """
        results = []
        
        short_period = self.get_config_value('short_period', 20)
        long_period = self.get_config_value('long_period', 50)
        volume_confirm = self.get_config_value('volume_confirm', True)
        
        for ticker, df in data.items():
            # 验证数据
            required_cols = ['close', 'volume']
            if not self.validate_data(df, required_cols):
                continue
            
            # 确保有足够的数据
            if len(df) < long_period + 1:
                continue
            
            try:
                # 计算均线
                short_ma_col = f'sma_{short_period}'
                long_ma_col = f'sma_{long_period}'
                
                if short_ma_col not in df.columns or long_ma_col not in df.columns:
                    self.logger.debug(f"{ticker}: 缺少均线数据")
                    continue
                
                # 获取最新和前一天的数据
                latest = self.get_latest_row(df)
                previous = self.get_previous_row(df)
                
                if latest is None or previous is None:
                    continue
                
                # 检测金叉：短均线从下方穿过长均线
                short_ma_now = latest[short_ma_col]
                long_ma_now = latest[long_ma_col]
                short_ma_prev = previous[short_ma_col]
                long_ma_prev = previous[long_ma_col]
                
                # 判断是否发生金叉
                golden_cross = (
                    short_ma_prev <= long_ma_prev and  # 前一天短均线在下方
                    short_ma_now > long_ma_now          # 今天短均线在上方
                )
                
                if golden_cross:
                    # 如果需要成交量确认
                    if volume_confirm and 'volume_ratio' in df.columns:
                        if latest['volume_ratio'] < 1.0:
                            continue
                    
                    price = latest['close']
                    details = {
                        'short_ma': round(short_ma_now, 2),
                        'long_ma': round(long_ma_now, 2),
                        'volume_ratio': round(latest.get('volume_ratio', 0), 2)
                    }
                    
                    results.append({
                        'ticker': ticker,
                        'signal': '均线金叉',
                        'price': round(price, 2),
                        'details': details
                    })
                    
                    self.log_signal(ticker, '均线金叉', str(details))
                    
            except Exception as e:
                self.logger.error(f"处理 {ticker} 时出错: {e}")
        
        return results


class VolumeSurgeStrategy(BaseStrategy):
    """
    成交量异常策略
    检测成交量异常放大且价格上涨的股票
    """
    
    def __init__(self, config: Dict = None):
        default_config = {
            'lookback_period': 20,
            'surge_multiplier': 2.0,
            'min_price_change': 2.0  # 最小涨幅百分比
        }
        if config:
            default_config.update(config)
        
        super().__init__("Volume_Surge", default_config)
    
    def scan(self, data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """
        扫描成交量异常信号
        """
        results = []
        
        surge_multiplier = self.get_config_value('surge_multiplier', 2.0)
        min_price_change = self.get_config_value('min_price_change', 2.0)
        
        for ticker, df in data.items():
            required_cols = ['close', 'volume']
            if not self.validate_data(df, required_cols):
                continue
            
            try:
                latest = self.get_latest_row(df)
                if latest is None:
                    continue
                
                # 检查是否有成交量比率数据
                if 'volume_ratio' not in df.columns:
                    continue
                
                volume_ratio = latest['volume_ratio']
                
                # 成交量放大
                if volume_ratio >= surge_multiplier:
                    # 检查价格变化
                    if 'price_change_1d' in df.columns:
                        price_change = latest['price_change_1d']
                        
                        # 价格上涨
                        if price_change >= min_price_change:
                            details = {
                                'volume_ratio': round(volume_ratio, 2),
                                'price_change': round(price_change, 2),
                                'volume': int(latest['volume'])
                            }
                            
                            results.append({
                                'ticker': ticker,
                                'signal': '成交量放大',
                                'price': round(latest['close'], 2),
                                'details': details
                            })
                            
                            self.log_signal(ticker, '成交量放大', str(details))
                            
            except Exception as e:
                self.logger.error(f"处理 {ticker} 时出错: {e}")
        
        return results


class BreakoutStrategy(BaseStrategy):
    """
    突破策略
    检测价格突破近期高点的股票
    """
    
    def __init__(self, config: Dict = None):
        default_config = {
            'lookback_period': 20,
            'volume_confirm': True,
            'min_volume_ratio': 1.2
        }
        if config:
            default_config.update(config)
        
        super().__init__("Breakout", default_config)
    
    def scan(self, data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """
        扫描突破信号
        """
        results = []
        
        lookback_period = self.get_config_value('lookback_period', 20)
        volume_confirm = self.get_config_value('volume_confirm', True)
        min_volume_ratio = self.get_config_value('min_volume_ratio', 1.2)
        
        for ticker, df in data.items():
            required_cols = ['close', 'high', 'volume']
            if not self.validate_data(df, required_cols):
                continue
            
            if len(df) < lookback_period + 1:
                continue
            
            try:
                latest = self.get_latest_row(df)
                if latest is None:
                    continue
                
                # 计算前N天的最高价（不包括今天）
                recent_high = df['high'].iloc[-(lookback_period+1):-1].max()
                current_close = latest['close']
                
                # 检测突破
                if current_close > recent_high:
                    # 成交量确认
                    if volume_confirm and 'volume_ratio' in df.columns:
                        if latest['volume_ratio'] < min_volume_ratio:
                            continue
                    
                    breakout_pct = ((current_close - recent_high) / recent_high) * 100
                    
                    details = {
                        'recent_high': round(recent_high, 2),
                        'breakout_pct': round(breakout_pct, 2),
                        'volume_ratio': round(latest.get('volume_ratio', 0), 2)
                    }
                    
                    results.append({
                        'ticker': ticker,
                        'signal': '价格突破',
                        'price': round(current_close, 2),
                        'details': details
                    })
                    
                    self.log_signal(ticker, '价格突破', str(details))
                    
            except Exception as e:
                self.logger.error(f"处理 {ticker} 时出错: {e}")
        
        return results


class RSIStrategy(BaseStrategy):
    """
    RSI策略
    检测超卖反弹机会
    """
    
    def __init__(self, config: Dict = None):
        default_config = {
            'oversold_threshold': 30,
            'overbought_threshold': 70,
            'mode': 'oversold'  # oversold 或 overbought
        }
        if config:
            default_config.update(config)
        
        super().__init__("RSI", default_config)
    
    def scan(self, data: Dict[str, pd.DataFrame]) -> List[Dict]:
        """
        扫描RSI信号
        """
        results = []
        
        oversold_threshold = self.get_config_value('oversold_threshold', 30)
        overbought_threshold = self.get_config_value('overbought_threshold', 70)
        mode = self.get_config_value('mode', 'oversold')
        
        for ticker, df in data.items():
            required_cols = ['close', 'rsi']
            if not self.validate_data(df, required_cols):
                continue
            
            try:
                latest = self.get_latest_row(df)
                previous = self.get_previous_row(df)
                
                if latest is None or previous is None:
                    continue
                
                rsi_now = latest['rsi']
                rsi_prev = previous['rsi']
                
                if pd.isna(rsi_now) or pd.isna(rsi_prev):
                    continue
                
                signal_detected = False
                signal_type = ""
                
                # 超卖反弹
                if mode == 'oversold':
                    if rsi_prev <= oversold_threshold and rsi_now > oversold_threshold:
                        signal_detected = True
                        signal_type = "RSI超卖反弹"
                
                # 超买回落
                elif mode == 'overbought':
                    if rsi_prev >= overbought_threshold and rsi_now < overbought_threshold:
                        signal_detected = True
                        signal_type = "RSI超买回落"
                
                if signal_detected:
                    details = {
                        'rsi': round(rsi_now, 2),
                        'rsi_prev': round(rsi_prev, 2)
                    }
                    
                    results.append({
                        'ticker': ticker,
                        'signal': signal_type,
                        'price': round(latest['close'], 2),
                        'details': details
                    })
                    
                    self.log_signal(ticker, signal_type, str(details))
                    
            except Exception as e:
                self.logger.error(f"处理 {ticker} 时出错: {e}")
        
        return results

