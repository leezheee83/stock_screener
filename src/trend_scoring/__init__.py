"""
Trend Scoring - 趋势评分系统
可插拔的趋势评分器
"""

from .base_scorer import BaseTrendScorer
from .ma_adx_scorer import MAADXScorer

__all__ = ['BaseTrendScorer', 'MAADXScorer']








