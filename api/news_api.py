"""
news_api.py — 新闻数据获取模块

支持两种新闻源：
1. 聚合数据 API（juhe.cn）- 需要 NEWS_KEY
2. RSS 订阅源（无需 Key）

自动降级：NEWS_KEY 有则用 API，没有则用 RSS。
RSS 失败时不影响整体流程（仅该分类无新闻）。

实现方：芦泓天
"""

import logging
import requests
import feedparser  # 用于解析 RSS
import socket
from typing import Optional
from datetime import datetime

from config.settings import settings
from config.constants import (
    NEWS_CATEGORIES,
    DEFAULT_NEWS_LIMIT,
    API_TIMEOUT,
)
from models.news import NewsItem

# 设置超时
socket.setdefaulttimeout(API_TIMEOUT)

logger = logging.getLogger(__name__)


class NewsAPIError(Exception):
    """新闻 API 请求异常"""
    pass


# RSS 源列表（按优先级排序）
RSS_SOURCES = {
    "科技": [
        "https://www.ithome.com/rss/",
        "https://www.oschina.net/news/rss",
        "https://www.36kr.com/feed",
    ],
    "财经": [
        # 国内财经 RSS 大多失效，备用综合源作为兜底
        "http://www.people.com.cn/rss/finance.xml",
    ],
    "体育": [
        "http://www.people.com.cn/rss/sports.xml",
    ],
    "综合": [
        "http://www.people.com.cn/rss/politics.xml",
        "http://www.people.com.cn/rss/leader.xml",
        "https://www.ithome.com/rss/",  # IT 之家也包含综合资讯
    ],
}


def fetch_news(
    categories: list = None,
    limit: int = DEFAULT_NEWS_LIMIT,
) -> list:
    """按类别获取新闻列表

    策略：
        1. 优先使用聚合数据 API（如果有 NEWS_KEY）
        2. 否则使用 RSS 源（无需 Key）
        3. 失败时记录错误但不中断

    Args:
        categories: 新闻分类列表
        limit: 最大返回条数

    Returns:
        NewsItem 列表

    Raises:
        NewsAPIError: 当所有数据源都失败时抛出
    """
    categories = categories or NEWS_CATEGORIES
    all_items = []

    # 策略 1：尝试聚合数据 API
    api_key = settings.get("NEWS_KEY")
    if api_key:
        logger.info("使用聚合数据 API 获取新闻")
        for category in categories:
            try:
                items = _fetch_juhe_news(api_key, category, limit)
                all_items.extend(items)
            except Exception as e:
                logger.warning("聚合数据 API 失败: category=%s, error=%s", category, str(e))
        if all_items:
            return _dedupe_and_truncate(all_items, limit, categories)

    # 策略 2：使用 RSS 源（无需 Key）
    logger.info("使用 RSS 源获取新闻（无需 API Key）")
    for category in categories:
        items = _fetch_rss_news(category, limit)
        if items:
            all_items.extend(items)
            logger.info("RSS 获取成功: category=%s, count=%d", category, len(items))
        else:
            logger.warning("RSS 无内容: category=%s", category)

    if not all_items:
        raise NewsAPIError("所有新闻源都不可用")

    return _dedupe_and_truncate(all_items, limit, categories)


def _dedupe_and_truncate(items: list, limit: int, categories: list) -> list:
    """去重并截断"""
    seen_titles = set()
    unique = []
    for item in items:
        if item.title and item.title not in seen_titles:
            seen_titles.add(item.title)
            unique.append(item)

    # 每个分类平均分配条数
    per_category = max(1, limit)
    result = unique[:limit * len(categories)]
    logger.info("新闻获取完成: total=%d, after_filter=%d", len(items), len(result))
    return result


def _fetch_juhe_news(api_key: str, category: str, limit: int) -> list:
    """聚合数据新闻 API"""
    url = "http://v.juhe.cn/toutiao/index"
    params = {
        "key": api_key,
        "type": _map_category(category),
    }
    try:
        response = requests.get(
            url,
            params=params,
            timeout=API_TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        response.raise_for_status()
        data = response.json()

        if data.get("error_code", 0) != 0:
            raise NewsAPIError(f"新闻接口返回错误: {data}")

        articles = data.get("result", {}).get("data", [])

        items = []
        for article in articles[:limit]:
            items.append(NewsItem(
                title=article.get("title", ""),
                summary=article.get("digest", ""),
                source=article.get("author_name", ""),
                category=category,
                url=article.get("url", ""),
                publish_time=article.get("date", ""),
            ))
        return items
    except Exception as e:
        raise NewsAPIError(f"新闻请求异常: {e}")


def _fetch_rss_news(category: str, limit: int) -> list:
    """从 RSS 源获取新闻"""
    items = []
    sources = RSS_SOURCES.get(category, [])

    for url in sources:
        if len(items) >= limit:
            break
        try:
            source_items = _parse_rss(url, category, limit - len(items))
            items.extend(source_items)
        except Exception as e:
            logger.warning("RSS 失败: %s, error=%s", url, str(e)[:80])
            continue

    return items[:limit]


def _parse_rss(url: str, category: str, limit: int) -> list:
    """解析 RSS 源"""
    try:
        # 使用 requests 拉取 RSS（避免 feedparser 直接访问时的 SSL 问题）
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, timeout=API_TIMEOUT, headers=headers)
        response.raise_for_status()

        # 解析
        feed = feedparser.parse(response.content)
        if not feed.entries:
            return []

        items = []
        for entry in feed.entries[:limit]:
            # 提取发布时间
            publish_time = ""
            for attr in ("published", "updated", "created"):
                if hasattr(entry, attr):
                    publish_time = getattr(entry, attr)
                    break

            # 提取摘要（去掉 HTML 标签）
            summary = ""
            for attr in ("summary", "description"):
                if hasattr(entry, attr):
                    summary = _strip_html(getattr(entry, attr))[:200]
                    break

            # 提取来源
            source = feed.feed.get("title", "RSS 新闻")

            title = entry.get("title", "").strip()
            if not title:
                continue

            items.append(NewsItem(
                title=title,
                summary=summary,
                source=source,
                category=category,
                url=entry.get("link", ""),
                publish_time=publish_time,
            ))

        return items
    except Exception as e:
        logger.error("RSS 解析失败: %s, error=%s", url, str(e)[:100])
        return []


def _strip_html(text: str) -> str:
    """简单去除 HTML 标签"""
    import re
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", "", text)
    return clean.strip()


def _map_category(category: str) -> str:
    """新闻分类映射（聚合数据用）"""
    category_map = {
        "科技": "keji",
        "财经": "caijing",
        "体育": "tiyu",
        "综合": "top",
    }
    return category_map.get(category, "top")
