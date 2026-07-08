"""
brief.py — 简报数据模型

定义 BriefReport 标准数据类，是 AI 生成和前端展示的核心数据结构。
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional

from models.news import NewsItem


@dataclass
class BriefReport:
    """晨间简报标准结构

    这是整个项目的核心输出数据结构。AI 模块生成此对象，
    前端展示此对象，存储模块保存此对象。

    Attributes:
        date: 简报日期，格式 YYYY-MM-DD
        city: 目标城市
        weather_summary: AI 生成的天气摘要（自然语言一段话）
        news_items: 关联新闻列表
        digest: AI 生成的简报正文（核心内容）
        model_used: 使用的模型: deepseek / zhipu / qwen
        created_at: 创建时间
    """

    date: str = ""
    city: str = ""
    weather_summary: str = ""
    news_items: list = field(default_factory=list)
    digest: str = ""
    model_used: str = "deepseek"
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """转为字典格式（含嵌套序列化）"""
        d = asdict(self)
        if isinstance(d.get("created_at"), datetime):
            d["created_at"] = d["created_at"].strftime("%Y-%m-%dT%H:%M:%S")
        # 嵌套 NewsItem 序列化为 dict
        d["news_items"] = [
            item.to_dict() if hasattr(item, "to_dict") else item
            for item in d["news_items"]
        ]
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "BriefReport":
        """从字典创建实例（含嵌套反序列化）"""
        ts = data.get("created_at")
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts)
            except ValueError:
                ts = datetime.now()

        raw_items = data.get("news_items", [])
        news_items = []
        for item in raw_items:
            if isinstance(item, NewsItem):
                news_items.append(item)
            elif isinstance(item, dict):
                news_items.append(NewsItem.from_dict(item))

        return cls(
            date=data.get("date", ""),
            city=data.get("city", ""),
            weather_summary=data.get("weather_summary", ""),
            news_items=news_items,
            digest=data.get("digest", ""),
            model_used=data.get("model_used", "deepseek"),
            created_at=ts,
        )

    def is_valid(self) -> bool:
        """校验简报数据完整性"""
        return bool(
            self.date
            and self.city
            and self.weather_summary
            and self.digest
        )

    def word_count(self) -> int:
        """返回简报字数统计"""
        total = len(self.weather_summary) + len(self.digest)
        for item in self.news_items:
            if hasattr(item, "summary"):
                total += len(item.summary)
        return total
