"""
news_api.py — 新闻数据获取模块

调用新闻 API 按类别获取新闻列表，
解析后返回标准化的 NewsItem 列表。

实现方：芦泓天
"""

import logging
from typing import Optional

from config.settings import settings
from config.constants import (
    NEWS_CATEGORIES,
    DEFAULT_NEWS_LIMIT,
    API_TIMEOUT,
)
from models.news import NewsItem

logger = logging.getLogger(__name__)


class NewsAPIError(Exception):
    """新闻 API 请求异常"""
    pass


def fetch_news(
    categories: list = None,
    limit: int = DEFAULT_NEWS_LIMIT,
) -> list:
    """按类别获取新闻列表

    步骤：
        1. 遍历每个分类，调用对应新闻 API
        2. 解析原始响应
        3. 转换为标准 NewsItem 对象列表
        4. 合并、按发布时间去重排序、截断到 limit 条

    Args:
        categories: 新闻分类列表，默认使用 NEWS_CATEGORIES
        limit: 最大返回条数，默认 5

    Returns:
        标准化 NewsItem 列表，最多 limit 条

    Raises:
        NewsAPIError: 当 API Key 未配置或请求失败时抛出
    """
    api_key = settings.get("NEWS_KEY")
    if not api_key:
        raise NewsAPIError("新闻 API Key (NEWS_KEY) 未配置，请在 .env 中设置")

    categories = categories or NEWS_CATEGORIES
    all_items = []

    for category in categories:
        try:
            items = _fetch_category_news(api_key, category, limit)
            all_items.extend(items)
            logger.info("获取新闻: category=%s, count=%d", category, len(items))
        except Exception as e:
            logger.error("获取新闻失败: category=%s, error=%s", category, str(e))
            # 单个分类失败不影响其他分类

    # 去重（按标题去重）
    seen_titles = set()
    unique_items = []
    for item in all_items:
        if item.title not in seen_titles:
            seen_titles.add(item.title)
            unique_items.append(item)

    # 截断到 limit 条
    result = unique_items[:limit * len(categories)]

    logger.info("新闻获取完成: total=%d, after_filter=%d", len(all_items), len(result))
    return result


def _fetch_category_news(api_key: str, category: str, limit: int) -> list:
    """获取单个分类的新闻

    Args:
        api_key: 新闻 API Key
        category: 分类名称
        limit: 该分类最大条数

    Returns:
        NewsItem 列表
    """
    # TODO: 芦泓天 — 实现新闻 API 请求
    # 根据实际使用的新闻 API 填写以下代码
    # 步骤：
    #   1. import requests
    #   2. resp = requests.get(新闻接口URL, params={"key": api_key, "category": category, "limit": limit}, timeout=API_TIMEOUT)
    #   3. resp.raise_for_status()
    #   4. data = resp.json()
    #   5. 遍历 data 中的文章，封装为 NewsItem 对象

    # 示例伪代码：
    # import requests
    # resp = requests.get(
    #     "https://example-news-api.com/articles",
    #     params={
    #         "key": api_key,
    #         "category": _map_category(category),
    #         "limit": limit,
    #     },
    #     timeout=API_TIMEOUT,
    # )
    # resp.raise_for_status()
    # articles = resp.json().get("articles", [])
    # items = []
    # for article in articles:
    #     items.append(NewsItem(
    #         title=article.get("title", ""),
    #         summary=article.get("description", ""),
    #         source=article.get("source", ""),
    #         category=category,
    #         url=article.get("url", ""),
    #         publish_time=article.get("publishedAt", ""),
    #     ))
    # return items

    raise NewsAPIError("新闻 API 接口待实现")


def _map_category(category: str) -> str:
    """将中文分类映射为 API 所需的分类标识

    Args:
        category: 中文分类名

    Returns:
        API 所需的分类字符串
    """
    # TODO: 芦泓天 — 根据实际 API 文档填写映射规则
    # 示例：
    # category_map = {
    #     "科技": "technology",
    #     "财经": "business",
    #     "体育": "sports",
    #     "综合": "general",
    # }
    # return category_map.get(category, "general")
    return category
