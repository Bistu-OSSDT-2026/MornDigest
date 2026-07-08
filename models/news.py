"""
news.py — 新闻数据模型

定义 NewsItem 标准数据类，所有新闻模块返回此类型的列表。
"""

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class NewsItem:
    """新闻条目标准结构

    所有新闻 API 调用模块（api/news_api.py）返回此类型的列表。

    Attributes:
        title: 标题
        summary: 摘要/导语
        source: 来源媒体名称
        category: 分类：科技 / 财经 / 体育 / 综合
        url: 原文链接
        publish_time: 发布时间
    """

    title: str = ""
    summary: str = ""
    source: str = ""
    category: str = "综合"
    url: str = ""
    publish_time: str = ""

    def to_dict(self) -> dict:
        """转为字典格式"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "NewsItem":
        """从字典创建实例"""
        return cls(
            title=data.get("title", ""),
            summary=data.get("summary", ""),
            source=data.get("source", ""),
            category=data.get("category", "综合"),
            url=data.get("url", ""),
            publish_time=data.get("publish_time", ""),
        )

    def is_valid(self) -> bool:
        """校验数据完整性 — 至少要有标题"""
        return bool(self.title)
