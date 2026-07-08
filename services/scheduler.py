"""
scheduler.py — 定时任务模块

支持定时自动拉取数据、生成简报。
当前为骨架实现，后续由拓展模块开发者完善。

实现方：刘诗钰
"""

import logging
import threading
from typing import Optional, Callable

logger = logging.getLogger(__name__)


class SimpleScheduler:
    """简易定时任务调度器

    使用 threading.Timer 实现基础定时功能。
    生产环境可替换为 APScheduler 等更强大的调度库。
    """

    def __init__(self):
        self._timer: Optional[threading.Timer] = None
        self._running = False
        self._callback: Optional[Callable] = None
        self._interval_seconds = 3600  # 默认每小时执行一次

    def start(
        self,
        callback: Callable,
        interval_seconds: int = 3600,
    ):
        """启动定时任务

        Args:
            callback: 定时执行的回调函数
            interval_seconds: 执行间隔（秒），默认 3600 (1小时)
        """
        self._callback = callback
        self._interval_seconds = interval_seconds
        self._running = True
        self._schedule_next()
        logger.info(
            "定时任务已启动, 间隔=%d秒", interval_seconds
        )

    def stop(self):
        """停止定时任务"""
        self._running = False
        if self._timer:
            self._timer.cancel()
            self._timer = None
        logger.info("定时任务已停止")

    def _schedule_next(self):
        """调度下一次执行"""
        if not self._running:
            return
        try:
            self._timer = threading.Timer(
                self._interval_seconds, self._execute_and_reschedule
            )
            self._timer.daemon = True
            self._timer.start()
        except Exception as e:
            logger.error("定时任务调度失败: %s", str(e))

    def _execute_and_reschedule(self):
        """执行回调并调度下一次"""
        try:
            logger.info("执行定时任务...")
            self._callback()
        except Exception as e:
            logger.error("定时任务执行失败: %s", str(e))
        finally:
            self._schedule_next()

    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._running


# 全局调度器单例
_scheduler = SimpleScheduler()


def start_scheduler(callback: Callable, interval_seconds: int = 3600):
    """启动全局定时任务

    Args:
        callback: 定时执行的回调函数
        interval_seconds: 执行间隔（秒）
    """
    _scheduler.start(callback, interval_seconds)


def stop_scheduler():
    """停止全局定时任务"""
    _scheduler.stop()


def is_scheduler_running() -> bool:
    """检查定时任务是否在运行"""
    return _scheduler.is_running
