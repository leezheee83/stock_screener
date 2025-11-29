#!/usr/bin/env python3
"""
Stock Screener - 美股定时筛选系统
主程序入口
"""

import os
import sys
import argparse
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import List, Dict

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config_manager import ConfigManager
from src.data_fetcher import DataFetcher
from src.data_storage import DataStorage
from src.indicators import TechnicalIndicators
from src.strategy import (
    MACrossoverStrategy, 
    VolumeSurgeStrategy, 
    BreakoutStrategy,
    RSIStrategy
)
from src.reporter import Reporter
from src.scheduler import TaskScheduler, ScheduleConfig


class StockScreener:
    """股票筛选系统主类"""
    
    def __init__(self, config_path: str = 'config/config.yaml'):
        """
        初始化筛选系统
        
        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        self.config_manager = ConfigManager(config_path)
        
        # 初始化日志
        self._setup_logging()
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("=" * 60)
        self.logger.info("股票筛选系统初始化")
        self.logger.info("=" * 60)
        
        # 初始化各模块（使用保守配置避免限流）
        self.data_fetcher = DataFetcher(
            history_days=self.config_manager.get_history_days(),
            max_workers=1,      # 串行下载（最安全，避免限流）
            request_delay=2.0,  # 每次请求间隔2秒
            max_retries=3       # 失败重试3次
        )
        self.data_storage = DataStorage()
        self.indicators = TechnicalIndicators()
        self.reporter = Reporter(
            output_dir=self.config_manager.get('report.output_dir', 'reports')
        )
        
        # 初始化策略
        self.strategies = self._initialize_strategies()
        
        self.logger.info(f"已启用 {len(self.strategies)} 个策略")
    
    def _setup_logging(self):
        """配置日志系统"""
        log_config = self.config_manager.get_logging_config()
        
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_format = log_config.get('format', 
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_file = log_config.get('file', 'logs/stock_screener.log')
        max_bytes = log_config.get('max_bytes', 10485760)
        backup_count = log_config.get('backup_count', 5)
        
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 配置根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # 文件处理器（带轮转）
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_formatter = logging.Formatter(log_format)
        console_handler.setFormatter(console_formatter)
        
        # 添加处理器
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
    
    def _initialize_strategies(self) -> List:
        """初始化策略列表"""
        strategies = []
        strategies_config = self.config_manager.get_strategies_config()
        
        # 均线交叉策略
        if strategies_config.get('ma_crossover', {}).get('enabled', False):
            strategies.append(MACrossoverStrategy(
                strategies_config.get('ma_crossover', {})
            ))
        
        # 成交量异常策略
        if strategies_config.get('volume_surge', {}).get('enabled', False):
            strategies.append(VolumeSurgeStrategy(
                strategies_config.get('volume_surge', {})
            ))
        
        # 突破策略
        if strategies_config.get('pattern_recognition', {}).get('enabled', False):
            strategies.append(BreakoutStrategy(
                strategies_config.get('pattern_recognition', {})
            ))
        
        # RSI策略（如果配置中有）
        if strategies_config.get('rsi', {}).get('enabled', False):
            strategies.append(RSIStrategy(
                strategies_config.get('rsi', {})
            ))
        
        return strategies
    
    def initialize_data(self):
        """初始化：首次下载所有历史数据"""
        self.logger.info("开始初始化数据...")
        
        # 获取股票列表
        stock_universe = self.config_manager.get_stock_universe()
        tickers = self.data_fetcher.get_stock_list(stock_universe)
        
        self.logger.info(f"股票池: {stock_universe}, 共 {len(tickers)} 只股票")
        
        # 获取所有周期的数据
        all_data = self.data_fetcher.fetch_all_timeframes(tickers)
        
        # 保存数据
        for period, data_dict in all_data.items():
            self.logger.info(f"保存 {period} 数据...")
            self.data_storage.save_multiple_stocks(data_dict, period)
        
        self.logger.info("数据初始化完成！")
        
        # 打印存储信息
        info = self.data_storage.get_storage_info()
        self.logger.info(f"存储统计: {info}")
    
    def update_data(self):
        """更新数据：增量下载最新数据"""
        self.logger.info("开始更新数据...")
        
        # 获取股票列表
        stock_universe = self.config_manager.get_stock_universe()
        tickers = self.data_fetcher.get_stock_list(stock_universe)
        
        # 对于每个周期，更新数据
        for period in self.config_manager.get_timeframes():
            self.logger.info(f"更新 {period} 数据...")
            data_dict = self.data_fetcher.fetch_multiple_stocks(tickers, period)
            self.data_storage.save_multiple_stocks(data_dict, period)
        
        self.logger.info("数据更新完成！")
    
    def run_screening(self) -> Dict[str, List[Dict]]:
        """执行股票筛选"""
        self.logger.info("=" * 60)
        self.logger.info("开始执行股票筛选")
        self.logger.info("=" * 60)
        
        # 加载数据（使用日K数据）
        available_stocks = self.data_storage.list_available_stocks('daily')
        self.logger.info(f"加载 {len(available_stocks)} 只股票的数据")
        
        stock_data = self.data_storage.load_multiple_stocks(available_stocks, 'daily')
        
        # 为每只股票计算技术指标
        self.logger.info("计算技术指标...")
        indicators_config = self.config_manager.get_indicators_config()
        
        for ticker in stock_data.keys():
            stock_data[ticker] = self.indicators.add_all_indicators(
                stock_data[ticker], 
                indicators_config
            )
        
        # 执行每个策略
        all_results = {}
        
        for strategy in self.strategies:
            self.logger.info(f"执行策略: {strategy.name}")
            results = strategy.scan(stock_data)
            all_results[strategy.name] = results
            self.logger.info(f"策略 {strategy.name} 找到 {len(results)} 只股票")
        
        return all_results
    
    def run_once(self):
        """执行一次完整的筛选流程"""
        self.logger.info("执行一次性筛选任务")
        
        # 更新数据
        self.update_data()
        
        # 执行筛选
        all_results = self.run_screening()
        
        # 生成报告
        report_config = self.config_manager.get_report_config()
        report_path = self.reporter.generate_summary_report(
            all_results,
            format=report_config.get('format', 'both')
        )
        
        if report_path:
            self.logger.info(f"报告已生成: {report_path}")
        
        # 打印摘要
        self._print_summary(all_results)
        
        return all_results
    
    def _print_summary(self, all_results: Dict[str, List[Dict]]):
        """打印筛选结果摘要"""
        self.logger.info("=" * 60)
        self.logger.info("筛选结果摘要")
        self.logger.info("=" * 60)
        
        total_signals = 0
        for strategy_name, results in all_results.items():
            count = len(results)
            total_signals += count
            self.logger.info(f"{strategy_name:20s}: {count:3d} 个信号")
            
            # 打印前3个结果
            for i, result in enumerate(results[:3]):
                self.logger.info(f"  - {result['ticker']:6s} ${result['price']:7.2f} {result['signal']}")
        
        self.logger.info("=" * 60)
        self.logger.info(f"总计: {total_signals} 个信号")
        self.logger.info("=" * 60)
    
    def start_scheduler(self):
        """启动定时任务"""
        self.logger.info("启动定时调度器...")
        
        scheduler_config = self.config_manager.get_scheduler_config()
        
        if not scheduler_config.get('enabled', True):
            self.logger.warning("调度器未启用")
            return
        
        # 创建调度器
        scheduler = TaskScheduler()
        
        # 添加定时任务
        schedules = scheduler_config.get('schedules', [])
        for schedule_item in schedules:
            time_str = schedule_item.get('time')
            timezone = schedule_item.get('timezone', 'US/Eastern')
            
            scheduler.add_daily_job(
                self.run_once,
                time_str,
                timezone
            )
        
        # 启动调度器
        self.logger.info("调度器已配置，开始运行...")
        scheduler.start()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='美股定时筛选系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py --init          # 初始化，下载历史数据
  python main.py --run-once      # 手动执行一次筛选
  python main.py --daemon        # 启动定时任务（后台运行）
  python main.py --update        # 更新数据
        """
    )
    
    parser.add_argument('--init', action='store_true',
                       help='初始化系统，下载历史数据')
    parser.add_argument('--run-once', action='store_true',
                       help='手动执行一次筛选')
    parser.add_argument('--daemon', action='store_true',
                       help='启动定时任务')
    parser.add_argument('--update', action='store_true',
                       help='仅更新数据，不执行筛选')
    parser.add_argument('--config', type=str, default='config/config.yaml',
                       help='配置文件路径')
    
    args = parser.parse_args()
    
    # 创建系统实例
    screener = StockScreener(config_path=args.config)
    
    # 根据参数执行相应操作
    if args.init:
        screener.initialize_data()
    elif args.update:
        screener.update_data()
    elif args.run_once:
        screener.run_once()
    elif args.daemon:
        screener.start_scheduler()
    else:
        # 默认：显示帮助信息
        parser.print_help()
        print("\n提示: 首次使用请先运行 'python main.py --init' 初始化数据")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序已停止")
        sys.exit(0)
    except Exception as e:
        logging.error(f"程序异常: {e}", exc_info=True)
        sys.exit(1)

