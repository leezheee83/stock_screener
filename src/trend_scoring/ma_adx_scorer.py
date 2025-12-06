"""
MA ADX Scorer - 均线+ADX趋势评分器
"""

from .base_scorer import BaseTrendScorer
import pandas as pd
from typing import Dict, List
import numpy as np


class MAADXScorer(BaseTrendScorer):
    """均线排列+ADX强度评分器"""
    
    VERSION = "1.0.0"
    NAME = "ma_adx"
    DESCRIPTION = "基于均线排列和ADX强度的趋势评分器"
    
    def __init__(self, config: dict):
        """
        初始化评分器
        
        Args:
            config: {
                'weights': {
                    'ma_alignment': 0.40,
                    'adx_strength': 0.35,
                    'price_momentum': 0.15,
                    'price_position': 0.10
                }
            }
        """
        super().__init__(config)
        self.weights = config.get('weights', {
            'ma_alignment': 0.40,
            'adx_strength': 0.35,
            'price_momentum': 0.15,
            'price_position': 0.10
        })
    
    def score(self, df: pd.DataFrame) -> Dict:
        """
        计算趋势得分
        
        Args:
            df: 包含技术指标的DataFrame
        
        Returns:
            Dict: 评分结果
        """
        if df is None or df.empty:
            return self._empty_score()
        
        latest = df.iloc[-1]
        
        # 1. 均线排列得分 (0-100)
        ma_score, ma_details = self._score_ma_alignment(latest)
        
        # 2. ADX强度得分 (0-100)
        adx_score, adx_details = self._score_adx_strength(latest)
        
        # 3. 价格动量得分 (0-100)
        momentum_score, momentum_details = self._score_price_momentum(latest)
        
        # 4. 价格位置得分 (0-100)
        position_score, position_details = self._score_price_position(df)
        
        # 加权总分
        total = (
            ma_score * self.weights['ma_alignment'] +
            adx_score * self.weights['adx_strength'] +
            momentum_score * self.weights['price_momentum'] +
            position_score * self.weights['price_position']
        )
        
        return {
            'total': round(total, 2),
            'components': {
                'ma_alignment': {
                    'score': round(ma_score, 2),
                    'weight': self.weights['ma_alignment'],
                    'weighted_score': round(ma_score * self.weights['ma_alignment'], 2),
                    'details': ma_details
                },
                'adx_strength': {
                    'score': round(adx_score, 2),
                    'weight': self.weights['adx_strength'],
                    'weighted_score': round(adx_score * self.weights['adx_strength'], 2),
                    'details': adx_details
                },
                'price_momentum': {
                    'score': round(momentum_score, 2),
                    'weight': self.weights['price_momentum'],
                    'weighted_score': round(momentum_score * self.weights['price_momentum'], 2),
                    'details': momentum_details
                },
                'price_position': {
                    'score': round(position_score, 2),
                    'weight': self.weights['price_position'],
                    'weighted_score': round(position_score * self.weights['price_position'], 2),
                    'details': position_details
                }
            },
            'pass_threshold': total >= 50.0,
            'details': {
                'scorer': self.NAME,
                'version': self.VERSION
            }
        }
    
    def _score_ma_alignment(self, latest: pd.Series) -> tuple:
        """
        评估均线排列 (0-100分)
        
        Args:
            latest: 最新一行数据
        
        Returns:
            tuple: (score, details)
        """
        ma5 = latest.get('sma_5', 0)
        ma10 = latest.get('sma_10', 0)
        ma20 = latest.get('sma_20', 0)
        ma50 = latest.get('sma_50', 0)
        price = latest['close']
        
        # 检查数据有效性
        if pd.isna(ma5) or pd.isna(ma10) or pd.isna(ma20) or pd.isna(ma50):
            return 0, {'status': 'no_data', 'error': 'Missing MA data'}
        
        # 检查多头排列
        alignment_count = 0
        if price > ma5: alignment_count += 1
        if ma5 > ma10: alignment_count += 1
        if ma10 > ma20: alignment_count += 1
        if ma20 > ma50: alignment_count += 1
        
        # 计算得分
        if alignment_count == 4:
            score = 100  # 完美多头排列
            status = "perfect_bullish"
        elif alignment_count == 3:
            score = 75   # 三线多头
            status = "strong_bullish"
        elif alignment_count == 2:
            score = 50   # 两线多头
            status = "moderate_bullish"
        elif alignment_count == 1:
            score = 25
            status = "weak_bullish"
        else:
            score = 0
            status = "no_alignment"
        
        details = {
            'status': status,
            'alignment_count': alignment_count,
            'price': round(float(price), 2),
            'ma5': round(float(ma5), 2),
            'ma10': round(float(ma10), 2),
            'ma20': round(float(ma20), 2),
            'ma50': round(float(ma50), 2)
        }
        
        return score, details
    
    def _score_adx_strength(self, latest: pd.Series) -> tuple:
        """
        评估ADX强度 (0-100分)
        
        Args:
            latest: 最新一行数据
        
        Returns:
            tuple: (score, details)
        """
        adx = latest.get('adx', np.nan)
        plus_di = latest.get('plus_di', np.nan)
        minus_di = latest.get('minus_di', np.nan)
        
        # ADX评分规则
        if pd.isna(adx) or pd.isna(plus_di) or pd.isna(minus_di):
            return 0, {'status': 'no_data', 'adx': None}
        
        # 必须是上涨趋势
        if plus_di <= minus_di:
            score = 0
            status = "downtrend"
        # ADX理想区间 25-40
        elif 25 <= adx <= 40:
            score = 100
            status = "strong_uptrend"
        # ADX过高可能过热
        elif 40 < adx <= 50:
            score = 70
            status = "very_strong_uptrend"
        elif adx > 50:
            score = 50
            status = "overheated"
        # ADX 20-25 趋势形成中
        elif 20 <= adx < 25:
            score = 60
            status = "forming_uptrend"
        # ADX太低，无明确趋势
        else:
            score = 30
            status = "weak_trend"
        
        details = {
            'status': status,
            'adx': round(float(adx), 2),
            'plus_di': round(float(plus_di), 2),
            'minus_di': round(float(minus_di), 2),
            'di_diff': round(float(plus_di - minus_di), 2)
        }
        
        return score, details
    
    def _score_price_momentum(self, latest: pd.Series) -> tuple:
        """
        评估价格动量 (0-100分)
        
        Args:
            latest: 最新一行数据
        
        Returns:
            tuple: (score, details)
        """
        # 使用5日涨跌幅作为动量指标
        return_5d = latest.get('price_change_5d', 0)
        
        if pd.isna(return_5d):
            return 0, {'status': 'no_data', 'return_pct': None}
        
        # 评分规则
        if return_5d >= 10:
            score = 100
            status = "strong_momentum"
        elif return_5d >= 5:
            score = 70
            status = "good_momentum"
        elif return_5d >= 2:
            score = 50
            status = "moderate_momentum"
        elif return_5d >= 0:
            score = 30
            status = "weak_momentum"
        else:
            score = 0
            status = "negative_momentum"
        
        details = {
            'status': status,
            'return_pct': round(float(return_5d), 2)
        }
        
        return score, details
    
    def _score_price_position(self, df: pd.DataFrame) -> tuple:
        """
        评估价格相对位置 (0-100分)
        
        Args:
            df: 完整的DataFrame
        
        Returns:
            tuple: (score, details)
        """
        # 计算过去20天的高低点
        recent_20 = df.tail(20)
        
        if len(recent_20) < 20:
            return 50, {'position': 0.5, 'status': 'insufficient_data'}
        
        high_20 = recent_20['high'].max()
        low_20 = recent_20['low'].min()
        current_price = df.iloc[-1]['close']
        
        # 避免除零
        if high_20 == low_20:
            return 50, {'position': 0.5, 'status': 'flat'}
        
        # 相对位置 0-1
        position = (current_price - low_20) / (high_20 - low_20)
        
        # 评分规则：0.5-0.75是理想区间
        if 0.5 <= position <= 0.75:
            score = 100
            status = "ideal_position"
        elif 0.75 < position <= 0.85:
            score = 80
            status = "high_position"
        elif 0.3 <= position < 0.5:
            score = 60
            status = "mid_position"
        elif position > 0.85:
            score = 30
            status = "too_high"
        else:
            score = 20
            status = "low_position"
        
        details = {
            'status': status,
            'position': round(float(position), 3),
            'high_20d': round(float(high_20), 2),
            'low_20d': round(float(low_20), 2),
            'current': round(float(current_price), 2)
        }
        
        return score, details
    
    def get_required_indicators(self) -> List[str]:
        """返回需要的指标"""
        return [
            'close', 'high', 'low',
            'sma_5', 'sma_10', 'sma_20', 'sma_50',
            'adx', 'plus_di', 'minus_di',
            'price_change_5d'
        ]
    
    def _empty_score(self) -> Dict:
        """返回空数据的默认得分"""
        return {
            'total': 0,
            'components': {
                'ma_alignment': {'score': 0, 'weight': self.weights['ma_alignment'], 'weighted_score': 0, 'details': {}},
                'adx_strength': {'score': 0, 'weight': self.weights['adx_strength'], 'weighted_score': 0, 'details': {}},
                'price_momentum': {'score': 0, 'weight': self.weights['price_momentum'], 'weighted_score': 0, 'details': {}},
                'price_position': {'score': 0, 'weight': self.weights['price_position'], 'weighted_score': 0, 'details': {}}
            },
            'pass_threshold': False,
            'details': {'scorer': self.NAME, 'version': self.VERSION, 'error': 'empty_data'}
        }








