"""
config — 全局配置与常量模块

重新导出所有配置项和常量，支持直接 `from config import ...` 使用。
"""
from config.settings import settings
from config.constants import (
    CITIES,
    NEWS_CATEGORIES,
    AI_MODELS,
    DEFAULT_CITY,
    DEFAULT_MODEL,
    DEFAULT_CATEGORIES,
    DEFAULT_NEWS_LIMIT,
    DEFAULT_FORECAST_DAYS,
    DEFAULT_STORAGE_BACKEND,
    DATE_FORMAT,
    DATETIME_FORMAT,
    TIMESTAMP_FORMAT,
    API_TIMEOUT,
    APP_NAME,
    APP_VERSION,
    APP_DESCRIPTION,
)

__all__ = [
    "settings",
    "CITIES",
    "NEWS_CATEGORIES",
    "AI_MODELS",
    "DEFAULT_CITY",
    "DEFAULT_MODEL",
    "DEFAULT_CATEGORIES",
    "DEFAULT_NEWS_LIMIT",
    "DEFAULT_FORECAST_DAYS",
    "DEFAULT_STORAGE_BACKEND",
    "DATE_FORMAT",
    "DATETIME_FORMAT",
    "TIMESTAMP_FORMAT",
    "API_TIMEOUT",
    "APP_NAME",
    "APP_VERSION",
    "APP_DESCRIPTION",
]
