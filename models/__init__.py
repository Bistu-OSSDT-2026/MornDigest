"""
models — 全局数据模型

统一导出所有项目使用的标准数据结构类，
各模块间数据交互通过此类传递。
"""
from models.weather import WeatherData
from models.news import NewsItem
from models.brief import BriefReport
from models.prefs import UserPrefs

__all__ = ["WeatherData", "NewsItem", "BriefReport", "UserPrefs"]
