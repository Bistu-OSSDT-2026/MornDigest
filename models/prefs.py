"""
prefs.py — 用户偏好数据模型

定义 UserPrefs 标准数据类，存储与配置模块均使用此结构。
"""

from dataclasses import dataclass, asdict
from typing import Optional

from config.constants import DEFAULT_CITY, DEFAULT_MODEL, DEFAULT_CATEGORIES


@dataclass
class UserPrefs:
    """用户偏好标准结构

    用户通过前端设置页配置的偏好会被保存/加载为该对象。

    Attributes:
        city: 默认城市
        news_categories: 感兴趣的新闻分类列表
        ai_model: 首选 AI 模型: deepseek / zhipu / qwen
        briefing_time: 简报推送时间，格式 HH:MM
    """

    city: str = DEFAULT_CITY
    news_categories: list = None
    ai_model: str = DEFAULT_MODEL
    briefing_time: str = "08:00"

    def __post_init__(self):
        """初始化默认值"""
        if self.news_categories is None:
            self.news_categories = list(DEFAULT_CATEGORIES)

    def to_dict(self) -> dict:
        """转为字典格式"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "UserPrefs":
        """从字典创建实例"""
        return cls(
            city=data.get("city", DEFAULT_CITY),
            news_categories=data.get("news_categories", list(DEFAULT_CATEGORIES)),
            ai_model=data.get("ai_model", DEFAULT_MODEL),
            briefing_time=data.get("briefing_time", "08:00"),
        )

    @classmethod
    def default(cls) -> "UserPrefs":
        """返回默认偏好设置"""
        return cls()
