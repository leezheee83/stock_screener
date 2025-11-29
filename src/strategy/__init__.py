"""
Strategy module - 策略引擎模块
"""

from .base_strategy import BaseStrategy
from .builtin_strategies import (
    MACrossoverStrategy, 
    VolumeSurgeStrategy, 
    BreakoutStrategy,
    RSIStrategy
)

__all__ = [
    'BaseStrategy',
    'MACrossoverStrategy',
    'VolumeSurgeStrategy',
    'BreakoutStrategy',
    'RSIStrategy'
]

