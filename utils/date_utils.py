"""
date_utils.py — 日期工具函数

提供日期格式化、星期获取、友好时间等工具。
"""

from datetime import datetime, date, timedelta
from config.constants import DATE_FORMAT, DATETIME_FORMAT


def today() -> str:
    """返回今天日期字符串 YYYY-MM-DD"""
    return date.today().strftime(DATE_FORMAT)


def today_with_weekday() -> str:
    """返回含中文星期的日期，如 "2026-07-08 星期三" """
    weekday_map = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    d = date.today()
    return f"{d.strftime(DATE_FORMAT)} {weekday_map[d.weekday()]}"


def friendly_time(dt: datetime = None) -> str:
    """日期时间转换为友好显示

    Args:
        dt: datetime 对象，默认当前时间

    Returns:
        友好时间字符串，如 "今天 08:30", "昨天 14:20"
    """
    if dt is None:
        dt = datetime.now()
    now = datetime.now()
    delta = now - dt

    if delta.days == 0:
        return f"今天 {dt.strftime('%H:%M')}"
    elif delta.days == 1:
        return f"昨天 {dt.strftime('%H:%M')}"
    elif delta.days < 7:
        weekday_map = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        return f"{weekday_map[dt.weekday()]} {dt.strftime('%H:%M')}"
    else:
        return dt.strftime(DATETIME_FORMAT)


def add_days(d: str = None, days: int = 1) -> str:
    """在指定日期上增加 N 天

    Args:
        d: 日期字符串 YYYY-MM-DD，默认今天
        days: 增加天数

    Returns:
        新日期字符串
    """
    if d is None:
        base = date.today()
    else:
        base = datetime.strptime(d, DATE_FORMAT).date()
    return (base + timedelta(days=days)).strftime(DATE_FORMAT)


def format_timestamp(ts: float = None) -> str:
    """时间戳转友好字符串

    Args:
        ts: 时间戳，默认当前时间

    Returns:
        格式化日期时间字符串
    """
    if ts is None:
        ts = datetime.now().timestamp()
    dt = datetime.fromtimestamp(ts)
    return dt.strftime(DATETIME_FORMAT)
