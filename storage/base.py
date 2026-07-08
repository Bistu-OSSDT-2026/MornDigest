"""
base.py — 存储基类

定义所有存储后端必须实现的统一 CRUD 接口。
调用方通过此接口操作，不关心底层是 JSON 还是 SQLite。

调用方：services/brief_service.py, frontend/
实现方：崔锦崧
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional

from models.brief import BriefReport
from models.prefs import UserPrefs

logger = logging.getLogger(__name__)


class StorageError(Exception):
    """存储操作异常"""
    pass


class Storage(ABC):
    """存储基类

    所有存储后端（JSON/SQLite）必须继承此类并实现全部方法。
    """

    @abstractmethod
    def save_brief(self, brief: BriefReport) -> None:
        """保存简报到存储

        Args:
            brief: 简报数据对象
        """
        raise NotImplementedError

    @abstractmethod
    def get_brief(self, date: str) -> Optional[BriefReport]:
        """按日期获取简报

        Args:
            date: 日期字符串，格式 YYYY-MM-DD

        Returns:
            BriefReport 对象，不存在时返回 None
        """
        raise NotImplementedError

    @abstractmethod
    def list_briefs(self, limit: int = 10) -> list:
        """获取历史简报列表

        Args:
            limit: 最大返回条数，默认 10

        Returns:
            BriefReport 列表，按创建时间倒序排列
        """
        raise NotImplementedError

    @abstractmethod
    def save_prefs(self, prefs: UserPrefs) -> None:
        """保存用户偏好设置

        Args:
            prefs: 用户偏好对象
        """
        raise NotImplementedError

    @abstractmethod
    def load_prefs(self) -> UserPrefs:
        """加载用户偏好设置

        Returns:
            UserPrefs 对象，不存在时返回默认偏好
        """
        raise NotImplementedError
