"""
Scheduler - 定时调度器模块
管理定时任务的执行
"""

import logging
import schedule
import time
from datetime import datetime
from typing import Callable, List, Dict
import pytz


class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, timezone: str = 'US/Eastern'):
        """
        初始化任务调度器
        
        Args:
            timezone: 时区（默认美东时间）
        """
        self.timezone = pytz.timezone(timezone)
        self.logger = logging.getLogger(__name__)
        self.jobs = []
    
    def add_daily_job(self, func: Callable, time_str: str, timezone: str = None):
        """
        添加每日定时任务
        
        Args:
            func: 要执行的函数
            time_str: 时间字符串，格式 "HH:MM"
            timezone: 时区（可选，使用初始化时的时区）
        """
        if timezone:
            tz = pytz.timezone(timezone)
        else:
            tz = self.timezone
        
        # 创建包装函数，在正确时区执行
        def job_wrapper():
            current_time = datetime.now(tz)
            self.logger.info(f"执行定时任务: {func.__name__} at {current_time}")
            try:
                func()
                self.logger.info(f"任务 {func.__name__} 执行完成")
            except Exception as e:
                self.logger.error(f"任务 {func.__name__} 执行失败: {e}")
        
        # 添加到schedule
        job = schedule.every().day.at(time_str).do(job_wrapper)
        self.jobs.append(job)
        
        self.logger.info(f"已添加定时任务: {func.__name__} at {time_str} ({tz})")
    
    def add_interval_job(self, func: Callable, interval_minutes: int):
        """
        添加间隔执行的任务
        
        Args:
            func: 要执行的函数
            interval_minutes: 间隔分钟数
        """
        def job_wrapper():
            self.logger.info(f"执行间隔任务: {func.__name__}")
            try:
                func()
            except Exception as e:
                self.logger.error(f"间隔任务 {func.__name__} 执行失败: {e}")
        
        job = schedule.every(interval_minutes).minutes.do(job_wrapper)
        self.jobs.append(job)
        
        self.logger.info(f"已添加间隔任务: {func.__name__} every {interval_minutes} minutes")
    
    def add_weekly_job(self, func: Callable, day: str, time_str: str):
        """
        添加每周定时任务
        
        Args:
            func: 要执行的函数
            day: 星期几 (monday, tuesday, etc.)
            time_str: 时间字符串
        """
        def job_wrapper():
            self.logger.info(f"执行每周任务: {func.__name__}")
            try:
                func()
            except Exception as e:
                self.logger.error(f"每周任务 {func.__name__} 执行失败: {e}")
        
        day_map = {
            'monday': schedule.every().monday,
            'tuesday': schedule.every().tuesday,
            'wednesday': schedule.every().wednesday,
            'thursday': schedule.every().thursday,
            'friday': schedule.every().friday,
            'saturday': schedule.every().saturday,
            'sunday': schedule.every().sunday
        }
        
        if day.lower() in day_map:
            job = day_map[day.lower()].at(time_str).do(job_wrapper)
            self.jobs.append(job)
            self.logger.info(f"已添加每周任务: {func.__name__} on {day} at {time_str}")
        else:
            self.logger.error(f"无效的星期: {day}")
    
    def run_once(self, func: Callable):
        """
        立即执行一次任务
        
        Args:
            func: 要执行的函数
        """
        self.logger.info(f"立即执行任务: {func.__name__}")
        try:
            func()
            self.logger.info(f"任务 {func.__name__} 执行完成")
        except Exception as e:
            self.logger.error(f"任务 {func.__name__} 执行失败: {e}")
    
    def start(self, run_immediately: bool = False, test_func: Callable = None):
        """
        启动调度器（阻塞模式）
        
        Args:
            run_immediately: 是否立即执行一次所有任务
            test_func: 测试函数，如果提供则只运行一次后退出
        """
        if not self.jobs:
            self.logger.warning("没有任何任务被调度")
            return
        
        self.logger.info(f"调度器启动，共 {len(self.jobs)} 个任务")
        
        # 打印所有计划任务
        self.print_schedule()
        
        # 如果是测试模式
        if test_func:
            self.logger.info("测试模式：执行一次后退出")
            self.run_once(test_func)
            return
        
        # 如果需要立即运行
        if run_immediately:
            self.logger.info("立即执行所有任务一次")
            schedule.run_all()
        
        # 主循环
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            self.logger.info("调度器已停止")
    
    def start_non_blocking(self):
        """
        启动调度器（非阻塞模式）
        在后台线程中运行
        """
        import threading
        
        def run_scheduler():
            self.logger.info("调度器在后台线程中启动")
            try:
                while True:
                    schedule.run_pending()
                    time.sleep(60)
            except Exception as e:
                self.logger.error(f"调度器出错: {e}")
        
        thread = threading.Thread(target=run_scheduler, daemon=True)
        thread.start()
        self.logger.info("调度器已在后台启动")
    
    def print_schedule(self):
        """打印所有计划任务"""
        self.logger.info("=" * 50)
        self.logger.info("计划任务列表:")
        for job in schedule.jobs:
            self.logger.info(f"  - {job}")
        self.logger.info("=" * 50)
    
    def get_next_run_time(self) -> str:
        """
        获取下次运行时间
        
        Returns:
            str: 下次运行时间的描述
        """
        if not schedule.jobs:
            return "没有计划任务"
        
        next_run = schedule.idle_seconds()
        if next_run is None:
            return "未知"
        
        hours = int(next_run // 3600)
        minutes = int((next_run % 3600) // 60)
        
        return f"{hours}小时{minutes}分钟后"
    
    def clear_all_jobs(self):
        """清除所有任务"""
        schedule.clear()
        self.jobs = []
        self.logger.info("已清除所有任务")
    
    def is_market_hours(self, check_timezone: str = 'US/Eastern') -> bool:
        """
        检查当前是否在交易时间内
        美股交易时间：周一至周五 09:30-16:00 ET
        
        Args:
            check_timezone: 检查的时区
        
        Returns:
            bool: 是否在交易时间
        """
        tz = pytz.timezone(check_timezone)
        now = datetime.now(tz)
        
        # 检查是否是工作日
        if now.weekday() >= 5:  # 周六(5)和周日(6)
            return False
        
        # 检查时间
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        return market_open <= now <= market_close
    
    def wait_until_market_close(self, timezone: str = 'US/Eastern'):
        """
        等待直到市场收盘
        
        Args:
            timezone: 时区
        """
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        
        # 如果已经收盘或非交易日，直接返回
        if not self.is_market_hours(timezone):
            self.logger.info("市场已收盘或非交易日")
            return
        
        # 计算到收盘的时间
        market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        wait_seconds = (market_close - now).total_seconds()
        
        if wait_seconds > 0:
            self.logger.info(f"等待市场收盘，剩余 {wait_seconds/60:.1f} 分钟")
            time.sleep(wait_seconds)


class ScheduleConfig:
    """调度配置辅助类"""
    
    # 美股市场时间点（美东时间）
    MARKET_OPEN = "09:30"
    MARKET_CLOSE = "16:00"
    AFTER_MARKET_CLOSE = "16:30"  # 收盘后30分钟，数据更新完成
    BEFORE_MARKET_OPEN = "09:00"  # 开盘前30分钟
    
    # 常用时区
    TIMEZONE_ET = "US/Eastern"
    TIMEZONE_PT = "US/Pacific"
    TIMEZONE_CST = "Asia/Shanghai"
    
    @staticmethod
    def get_market_schedule() -> List[Dict]:
        """
        获取建议的市场调度配置
        
        Returns:
            List[Dict]: 调度配置列表
        """
        return [
            {
                'time': ScheduleConfig.AFTER_MARKET_CLOSE,
                'timezone': ScheduleConfig.TIMEZONE_ET,
                'description': '美股收盘后，获取最新数据并筛选'
            },
            {
                'time': ScheduleConfig.BEFORE_MARKET_OPEN,
                'timezone': ScheduleConfig.TIMEZONE_ET,
                'description': '美股开盘前，再次筛选机会'
            }
        ]

