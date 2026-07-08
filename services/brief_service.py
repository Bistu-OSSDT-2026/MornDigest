"""
brief_service.py — 简报生成核心编排模块

串联 天气获取 → 新闻获取 → AI 生成 → 存储保存 完整流程。
是整个项目的中枢模块。

实现方：刘奕铮
"""

import logging
from datetime import datetime
from typing import Optional

from config.settings import settings
from config.constants import (
    DEFAULT_MODEL,
    DEFAULT_CATEGORIES,
    DEFAULT_CITY,
)
from models.weather import WeatherData
from models.news import NewsItem
from models.brief import BriefReport
from models.prefs import UserPrefs
from api.weather_api import fetch_weather, WeatherAPIError
from api.news_api import fetch_news, NewsAPIError
from ai.deepseek import DeepSeekBot
from ai.zhipu import ZhipuBot
from ai.qwen import QwenBot
from ai.base import AIModel, AModelError
from storage import create_storage

logger = logging.getLogger(__name__)

# 模型工厂映射
_MODEL_MAP = {
    "deepseek": DeepSeekBot,
    "zhipu": ZhipuBot,
    "qwen": QwenBot,
}


def get_ai_bot(model_name: str) -> AIModel:
    """根据模型名称获取对应的 AI 适配器实例

    Args:
        model_name: 模型标识 deepseek / zhipu / qwen

    Returns:
        AIModel 子类实例

    Raises:
        AModelError: 当模型名无效时抛出
    """
    bot_class = _MODEL_MAP.get(model_name)
    if bot_class is None:
        raise AModelError(
            f"不支持的 AI 模型: {model_name}，可选: {', '.join(_MODEL_MAP.keys())}"
        )
    return bot_class()


def generate_morning_brief(
    prefs: UserPrefs = None,
    city: str = None,
    model: str = None,
    categories: list = None,
    news_limit: int = 5,
) -> BriefReport:
    """按用户偏好执行完整简报生成流程

    流程:
        1. 获取天气数据 (调用 fetch_weather)
        2. 获取新闻数据 (调用 fetch_news)
        3. 调用 AI 模型生成简报 (调用 AIModel.generate_brief)
        4. 保存到存储 (调用 storage.save_brief)
        5. 返回 BriefReport

    参数优先级: 显式参数 > prefs 对象 > 默认值

    Args:
        prefs: 用户偏好对象（可省略，缺失时使用默认值）
        city: 城市名（覆盖 prefs.city）
        model: AI 模型名（覆盖 prefs.ai_model）
        categories: 新闻分类列表（覆盖 prefs.news_categories）
        news_limit: 新闻条数限制

    Returns:
        BriefReport: AI 生成的完整简报

    Raises:
        WeatherAPIError: 天气获取失败
        NewsAPIError: 新闻获取失败
        AModelError: AI 模型调用失败
    """
    # 参数优先级处理
    if prefs is None:
        prefs = UserPrefs.default()

    city = city or prefs.city or DEFAULT_CITY
    model = model or prefs.ai_model or DEFAULT_MODEL
    categories = categories or prefs.news_categories or DEFAULT_CATEGORIES

    logger.info(
        "开始生成简报: city=%s, model=%s, categories=%s", city, model, categories
    )

    # 步骤 1: 获取天气
    logger.info("步骤 1/4: 获取天气数据...")
    weather = fetch_weather(city)

    # 步骤 2: 获取新闻
    logger.info("步骤 2/4: 获取新闻数据...")
    news_list = fetch_news(categories, limit=news_limit)

    # 步骤 3: 调用 AI 生成简报
    logger.info("步骤 3/4: 调用 AI 模型 (%s) 生成简报...", model)
    bot = get_ai_bot(model)
    brief = bot.generate_brief(weather, news_list)

    # 步骤 4: 保存到存储
    logger.info("步骤 4/4: 保存简报...")
    try:
        storage = create_storage()
        storage.save_brief(brief)
    except Exception as e:
        logger.warning("保存简报失败（不影响展示）: %s", str(e))

    logger.info("简报生成完成: date=%s, city=%s", brief.date, brief.city)
    return brief


def get_recent_briefs(limit: int = 10) -> list:
    """获取最近的简报列表

    Args:
        limit: 最大返回条数

    Returns:
        BriefReport 列表
    """
    try:
        storage = create_storage()
        return storage.list_briefs(limit)
    except Exception as e:
        logger.error("获取历史简报失败: %s", str(e))
        return []
