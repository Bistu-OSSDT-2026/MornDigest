"""
storage — 数据持久化模块

提供统一的存储接口（JSON / SQLite 双后端）。
通过 create_storage() 工厂函数根据环境变量自动选择后端。

使用方式:
    from storage import create_storage
    storage = create_storage()  # 自动根据环境变量选择后端
    briefs = storage.list_briefs(limit=10)
"""
import logging

from config.constants import DEFAULT_STORAGE_BACKEND
from config.settings import settings
from storage.base import Storage, StorageError
from storage.json_store import JsonStore
from storage.sqlite_store import SqliteStore

logger = logging.getLogger(__name__)

__all__ = [
    "Storage",
    "StorageError",
    "JsonStore",
    "SqliteStore",
    "create_storage",
]


def create_storage() -> Storage:
    """存储后端工厂函数

    根据 STORAGE_BACKEND 环境变量选择存储后端：
        - json → JsonStore
        - sqlite → SqliteStore
        - 未配置时默认使用 json

    Returns:
        Storage 子类实例

    Example:
        >>> from storage import create_storage
        >>> storage = create_storage()
        >>> briefs = storage.list_briefs(limit=10)
    """
    backend = settings.get("STORAGE_BACKEND", DEFAULT_STORAGE_BACKEND).lower()

    if backend == "sqlite":
        logger.info("使用 SQLite 存储后端")
        return SqliteStore()

    # 默认 JSON
    logger.info("使用 JSON 存储后端")
    return JsonStore()
