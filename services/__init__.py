"""
services — 业务逻辑编排模块

提供简报生成核心流程和定时任务调度。
"""
from services.brief_service import (
    generate_morning_brief,
    get_ai_bot,
    get_recent_briefs,
)
from services.scheduler import (
    SimpleScheduler,
    start_scheduler,
    stop_scheduler,
    is_scheduler_running,
)

__all__ = [
    "generate_morning_brief",
    "get_ai_bot",
    "get_recent_briefs",
    "SimpleScheduler",
    "start_scheduler",
    "stop_scheduler",
    "is_scheduler_running",
]
