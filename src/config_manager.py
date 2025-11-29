"""
Config Manager - 配置管理模块
加载和管理配置文件
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List
import yaml


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(__name__)
        self.config = {}
        
        # 加载配置
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if not self.config_path.exists():
            self.logger.warning(f"配置文件不存在: {self.config_path}")
            self.config = self._get_default_config()
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            self.logger.info(f"已加载配置文件: {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            self.config = self._get_default_config()
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置值（支持嵌套键）
        
        Args:
            key_path: 键路径，使用点号分隔，如 "data.history_days"
            default: 默认值
        
        Returns:
            配置值或默认值
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_data_config(self) -> Dict:
        """获取数据配置"""
        return self.get('data', {})
    
    def get_scheduler_config(self) -> Dict:
        """获取调度器配置"""
        return self.get('scheduler', {})
    
    def get_strategies_config(self) -> Dict:
        """获取策略配置"""
        return self.get('strategies', {})
    
    def get_indicators_config(self) -> Dict:
        """获取技术指标配置"""
        return self.get('indicators', {})
    
    def get_report_config(self) -> Dict:
        """获取报告配置"""
        return self.get('report', {})
    
    def get_logging_config(self) -> Dict:
        """获取日志配置"""
        return self.get('logging', {})
    
    def is_strategy_enabled(self, strategy_name: str) -> bool:
        """
        检查策略是否启用
        
        Args:
            strategy_name: 策略名称
        
        Returns:
            bool: 是否启用
        """
        strategy_config = self.get(f'strategies.{strategy_name}', {})
        return strategy_config.get('enabled', False)
    
    def get_enabled_strategies(self) -> List[str]:
        """
        获取所有启用的策略列表
        
        Returns:
            List[str]: 启用的策略名称列表
        """
        strategies = self.get('strategies', {})
        enabled = []
        
        for name, config in strategies.items():
            if isinstance(config, dict) and config.get('enabled', False):
                enabled.append(name)
        
        return enabled
    
    def get_stock_universe(self) -> str:
        """获取股票池类型"""
        return self.get('data.stock_universe', 'sp500')
    
    def get_history_days(self) -> int:
        """获取历史数据天数"""
        return self.get('data.history_days', 180)
    
    def get_timeframes(self) -> List[str]:
        """获取时间周期列表"""
        return self.get('data.timeframes', ['daily', 'weekly', 'monthly'])
    
    def get_storage_paths(self) -> Dict[str, str]:
        """获取存储路径配置"""
        return self.get('data.storage', {
            'daily': 'data/daily',
            'weekly': 'data/weekly',
            'monthly': 'data/monthly'
        })
    
    def save_config(self, config_path: str = None):
        """
        保存配置到文件
        
        Args:
            config_path: 配置文件路径（可选）
        """
        if config_path:
            path = Path(config_path)
        else:
            path = self.config_path
        
        try:
            # 确保目录存在
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
            
            self.logger.info(f"配置已保存到: {path}")
            
        except Exception as e:
            self.logger.error(f"保存配置失败: {e}")
    
    def update_config(self, key_path: str, value: Any):
        """
        更新配置值
        
        Args:
            key_path: 键路径
            value: 新值
        """
        keys = key_path.split('.')
        config = self.config
        
        # 导航到目标位置
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # 设置值
        config[keys[-1]] = value
        self.logger.info(f"已更新配置: {key_path} = {value}")
    
    def _get_default_config(self) -> Dict:
        """
        获取默认配置
        
        Returns:
            Dict: 默认配置字典
        """
        return {
            'data': {
                'stock_universe': 'sp500',
                'history_days': 180,
                'timeframes': ['daily', 'weekly', 'monthly'],
                'storage': {
                    'daily': 'data/daily',
                    'weekly': 'data/weekly',
                    'monthly': 'data/monthly'
                }
            },
            'scheduler': {
                'enabled': True,
                'schedules': [
                    {'time': '16:30', 'timezone': 'US/Eastern'},
                    {'time': '09:00', 'timezone': 'US/Eastern'}
                ]
            },
            'strategies': {
                'ma_crossover': {
                    'enabled': True,
                    'short_period': 20,
                    'long_period': 50
                },
                'volume_surge': {
                    'enabled': True,
                    'lookback_period': 20,
                    'surge_multiplier': 2.0
                },
                'pattern_recognition': {
                    'enabled': False
                }
            },
            'indicators': {
                'ma_periods': [5, 10, 20, 50, 200],
                'ema_periods': [12, 26],
                'rsi_period': 14,
                'macd': {
                    'fast': 12,
                    'slow': 26,
                    'signal': 9
                },
                'bollinger_bands': {
                    'period': 20,
                    'std_dev': 2
                }
            },
            'report': {
                'format': 'both',
                'output_dir': 'reports',
                'include_details': True
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'logs/stock_screener.log',
                'max_bytes': 10485760,
                'backup_count': 5
            }
        }
    
    def print_config(self):
        """打印当前配置"""
        import json
        print("=" * 60)
        print("当前配置:")
        print("=" * 60)
        print(json.dumps(self.config, indent=2, ensure_ascii=False))
        print("=" * 60)

