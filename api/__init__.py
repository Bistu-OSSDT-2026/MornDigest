"""
api — 外部数据 API 模块

提供天气、新闻等外部数据源的统一调用入口。
"""
from api.weather_api import fetch_weather, WeatherAPIError
from api.news_api import fetch_news, NewsAPIError

__all__ = ["fetch_weather", "fetch_news", "WeatherAPIError", "NewsAPIError"]
