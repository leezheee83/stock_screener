"""
Technical Indicators - 技术指标计算模块
计算各类技术分析指标
"""

import logging
from typing import Optional, List
import pandas as pd
import numpy as np


class TechnicalIndicators:
    """技术指标计算器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    @staticmethod
    def calculate_sma(df: pd.DataFrame, period: int, column: str = 'close') -> pd.Series:
        """
        计算简单移动平均线 (SMA)
        
        Args:
            df: 数据DataFrame
            period: 周期
            column: 计算列名
        
        Returns:
            pd.Series: SMA值
        """
        return df[column].rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int, column: str = 'close') -> pd.Series:
        """
        计算指数移动平均线 (EMA)
        
        Args:
            df: 数据DataFrame
            period: 周期
            column: 计算列名
        
        Returns:
            pd.Series: EMA值
        """
        return df[column].ewm(span=period, adjust=False).mean()
    
    def calculate_multiple_ma(self, df: pd.DataFrame, periods: List[int]) -> pd.DataFrame:
        """
        计算多个周期的移动平均线
        
        Args:
            df: 数据DataFrame
            periods: 周期列表
        
        Returns:
            pd.DataFrame: 添加了MA列的DataFrame
        """
        df_result = df.copy()
        
        for period in periods:
            df_result[f'sma_{period}'] = self.calculate_sma(df, period)
            df_result[f'ema_{period}'] = self.calculate_ema(df, period)
        
        return df_result
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14, column: str = 'close') -> pd.Series:
        """
        计算相对强弱指标 (RSI)
        
        Args:
            df: 数据DataFrame
            period: 周期（默认14）
            column: 计算列名
        
        Returns:
            pd.Series: RSI值
        """
        delta = df[column].diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, 
                       signal: int = 9, column: str = 'close') -> tuple:
        """
        计算MACD指标
        
        Args:
            df: 数据DataFrame
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期
            column: 计算列名
        
        Returns:
            tuple: (MACD线, 信号线, MACD柱)
        """
        ema_fast = self.calculate_ema(df, fast, column)
        ema_slow = self.calculate_ema(df, slow, column)
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        macd_histogram = macd_line - signal_line
        
        return macd_line, signal_line, macd_histogram
    
    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, 
                                  std_dev: int = 2, column: str = 'close') -> tuple:
        """
        计算布林带
        
        Args:
            df: 数据DataFrame
            period: 周期
            std_dev: 标准差倍数
            column: 计算列名
        
        Returns:
            tuple: (中轨, 上轨, 下轨)
        """
        middle_band = df[column].rolling(window=period).mean()
        std = df[column].rolling(window=period).std()
        
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        
        return middle_band, upper_band, lower_band
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        计算平均真实波幅 (ATR)
        
        Args:
            df: 数据DataFrame
            period: 周期
        
        Returns:
            pd.Series: ATR值
        """
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def calculate_adx(df: pd.DataFrame, period: int = 14) -> tuple:
        """
        计算ADX指标 (Average Directional Index)
        
        Args:
            df: 数据DataFrame，必须包含high, low, close列
            period: 周期（默认14）
        
        Returns:
            tuple: (adx, plus_di, minus_di)
        """
        high = df['high']
        low = df['low']
        close = df['close']
        
        # 计算+DM和-DM
        high_diff = high.diff()
        low_diff = -low.diff()
        
        plus_dm = high_diff.copy()
        minus_dm = low_diff.copy()
        
        # +DM规则：high_diff > low_diff 且 high_diff > 0
        plus_dm[~((high_diff > low_diff) & (high_diff > 0))] = 0
        
        # -DM规则：low_diff > high_diff 且 low_diff > 0
        minus_dm[~((low_diff > high_diff) & (low_diff > 0))] = 0
        
        # 计算TR (True Range)
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # 平滑计算（使用Wilder's smoothing）
        atr = tr.ewm(alpha=1/period, adjust=False).mean()
        plus_di = 100 * (plus_dm.ewm(alpha=1/period, adjust=False).mean() / atr)
        minus_di = 100 * (minus_dm.ewm(alpha=1/period, adjust=False).mean() / atr)
        
        # 计算DX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        
        # 计算ADX（DX的移动平均）
        adx = dx.ewm(alpha=1/period, adjust=False).mean()
        
        return adx, plus_di, minus_di
    
    @staticmethod
    def calculate_volume_ma(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        计算成交量移动平均
        
        Args:
            df: 数据DataFrame
            period: 周期
        
        Returns:
            pd.Series: 成交量MA值
        """
        return df['volume'].rolling(window=period).mean()
    
    @staticmethod
    def calculate_volume_ratio(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        计算成交量比率（当前成交量 / 平均成交量）
        
        Args:
            df: 数据DataFrame
            period: 周期
        
        Returns:
            pd.Series: 成交量比率
        """
        volume_ma = df['volume'].rolling(window=period).mean()
        volume_ratio = df['volume'] / volume_ma
        
        return volume_ratio
    
    @staticmethod
    def calculate_price_change(df: pd.DataFrame, period: int = 1) -> pd.Series:
        """
        计算价格变化率
        
        Args:
            df: 数据DataFrame
            period: 周期
        
        Returns:
            pd.Series: 价格变化率（百分比）
        """
        return df['close'].pct_change(period) * 100
    
    @staticmethod
    def detect_ma_crossover(df: pd.DataFrame, short_period: int = 20, 
                           long_period: int = 50) -> pd.Series:
        """
        检测均线交叉
        
        Args:
            df: 数据DataFrame
            short_period: 短期均线周期
            long_period: 长期均线周期
        
        Returns:
            pd.Series: 1表示金叉（向上突破），-1表示死叉（向下突破），0表示无交叉
        """
        short_ma = df['close'].rolling(window=short_period).mean()
        long_ma = df['close'].rolling(window=long_period).mean()
        
        # 当前短均线是否在长均线上方
        above = (short_ma > long_ma).astype(int)
        # 检测变化
        crossover = above.diff()
        
        return crossover
    
    @staticmethod
    def detect_volume_surge(df: pd.DataFrame, period: int = 20, 
                           multiplier: float = 2.0) -> pd.Series:
        """
        检测成交量异常放大
        
        Args:
            df: 数据DataFrame
            period: 回看周期
            multiplier: 倍数阈值
        
        Returns:
            pd.Series: True表示成交量放大
        """
        volume_ma = df['volume'].rolling(window=period).mean()
        surge = df['volume'] > (volume_ma * multiplier)
        
        return surge
    
    @staticmethod
    def detect_breakout(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        检测价格突破（突破近期高点）
        
        Args:
            df: 数据DataFrame
            period: 回看周期
        
        Returns:
            pd.Series: True表示突破
        """
        # 计算前N天的最高价
        rolling_high = df['high'].rolling(window=period).max()
        # 检测当前收盘价是否突破前期高点
        breakout = df['close'] > rolling_high.shift(1)
        
        return breakout
    
    @staticmethod
    def detect_support_resistance(df: pd.DataFrame, period: int = 20, 
                                  threshold: float = 0.02) -> tuple:
        """
        检测支撑位和阻力位附近
        
        Args:
            df: 数据DataFrame
            period: 回看周期
            threshold: 价格偏离阈值（百分比）
        
        Returns:
            tuple: (接近支撑位, 接近阻力位)
        """
        rolling_low = df['low'].rolling(window=period).min()
        rolling_high = df['high'].rolling(window=period).max()
        
        # 当前价格距离支撑位/阻力位的距离
        distance_to_support = (df['close'] - rolling_low) / rolling_low
        distance_to_resistance = (rolling_high - df['close']) / df['close']
        
        near_support = distance_to_support < threshold
        near_resistance = distance_to_resistance < threshold
        
        return near_support, near_resistance
    
    def add_all_indicators(self, df: pd.DataFrame, config: dict = None) -> pd.DataFrame:
        """
        添加所有技术指标到DataFrame
        
        Args:
            df: 原始数据DataFrame
            config: 指标配置字典
        
        Returns:
            pd.DataFrame: 包含所有指标的DataFrame
        """
        if df is None or df.empty:
            return df
        
        df_result = df.copy()
        
        # 默认配置
        if config is None:
            config = {
                'ma_periods': [5, 10, 20, 50, 200],
                'rsi_period': 14,
                'macd': {'fast': 12, 'slow': 26, 'signal': 9},
                'bollinger': {'period': 20, 'std_dev': 2},
                'atr_period': 14,
                'volume_ma_period': 20
            }
        
        try:
            # 移动平均线
            if 'ma_periods' in config:
                for period in config['ma_periods']:
                    df_result[f'sma_{period}'] = self.calculate_sma(df_result, period)
                    df_result[f'ema_{period}'] = self.calculate_ema(df_result, period)
            
            # RSI
            if 'rsi_period' in config:
                df_result['rsi'] = self.calculate_rsi(df_result, config['rsi_period'])
            
            # MACD
            if 'macd' in config:
                macd_config = config['macd']
                macd, signal, hist = self.calculate_macd(
                    df_result, 
                    macd_config['fast'], 
                    macd_config['slow'], 
                    macd_config['signal']
                )
                df_result['macd'] = macd
                df_result['macd_signal'] = signal
                df_result['macd_hist'] = hist
            
            # 布林带
            if 'bollinger' in config:
                bb_config = config['bollinger']
                middle, upper, lower = self.calculate_bollinger_bands(
                    df_result, 
                    bb_config['period'], 
                    bb_config['std_dev']
                )
                df_result['bb_middle'] = middle
                df_result['bb_upper'] = upper
                df_result['bb_lower'] = lower
            
            # ATR
            if 'atr_period' in config:
                df_result['atr'] = self.calculate_atr(df_result, config['atr_period'])
            
            # ADX
            if 'adx_period' in config:
                adx, plus_di, minus_di = self.calculate_adx(df_result, config['adx_period'])
                df_result['adx'] = adx
                df_result['plus_di'] = plus_di
                df_result['minus_di'] = minus_di
            
            # 成交量指标
            if 'volume_ma_period' in config:
                df_result['volume_ma'] = self.calculate_volume_ma(
                    df_result, config['volume_ma_period']
                )
                df_result['volume_ratio'] = self.calculate_volume_ratio(
                    df_result, config['volume_ma_period']
                )
            
            # 价格变化
            df_result['price_change_1d'] = self.calculate_price_change(df_result, 1)
            df_result['price_change_5d'] = self.calculate_price_change(df_result, 5)
            
            self.logger.debug(f"已添加所有技术指标，共 {len(df_result.columns)} 列")
            
        except Exception as e:
            self.logger.error(f"计算技术指标时出错: {e}")
        
        return df_result

