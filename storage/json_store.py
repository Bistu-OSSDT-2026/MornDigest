"""
json_store.py — JSON 文件存储实现

使用本地 JSON 文件（data/store.json）存储简报和用户偏好。
适合轻量级、无需 SQL 的场景。

实现方：崔锦崧
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from models.brief import BriefReport
from models.news import NewsItem
from models.prefs import UserPrefs
from storage.base import Storage, StorageError

logger = logging.getLogger(__name__)

# 数据文件路径
DATA_DIR = Path(__file__).parent.parent / "data"
STORE_FILE = DATA_DIR / "store.json"


class JsonStore(Storage):
    """JSON 文件存储后端"""

    def __init__(self, store_path: str = None):
        """初始化

        Args:
            store_path: 自定义存储文件路径，默认 data/store.json
        """
        self.store_path = Path(store_path) if store_path else STORE_FILE
        self._ensure_dir()

    def _ensure_dir(self):
        """确保数据目录存在"""
        self.store_path.parent.mkdir(parents=True, exist_ok=True)

    def _read_data(self) -> dict:
        """读取 JSON 文件数据

        Returns:
            完整数据字典 {"prefs": {...}, "briefs": [...]}
        """
        if not self.store_path.exists():
            return {"prefs": {}, "briefs": []}
        try:
            with open(self.store_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error("读取 JSON 存储失败: %s", str(e))
            return {"prefs": {}, "briefs": []}

    def _write_data(self, data: dict):
        """写入 JSON 文件

        写入前先备份已有文件，防止写入失败丢失数据。

        Args:
            data: 完整数据字典
        """
        # 备份现有文件
        if self.store_path.exists():
            backup = self.store_path.with_suffix(".json.bak")
            try:
                import shutil
                shutil.copy2(self.store_path, backup)
            except Exception as e:
                logger.warning("备份文件失败: %s", str(e))

        # 写入
        try:
            with open(self.store_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            logger.info("JSON 数据已保存: %s", self.store_path)
        except IOError as e:
            # 写入失败，尝试恢复备份
            backup = self.store_path.with_suffix(".json.bak")
            if backup.exists():
                try:
                    import shutil
                    shutil.copy2(backup, self.store_path)
                    logger.error("写入失败，已恢复备份")
                except Exception:
                    pass
            raise StorageError(f"保存 JSON 数据失败: {str(e)}")

    def save_brief(self, brief: BriefReport) -> None:
        """保存简报

        Args:
            brief: 简报对象
        """
        data = self._read_data()
        briefs = data.get("briefs", [])

        # 检查是否已有同一天的简报，有则更新
        for i, b in enumerate(briefs):
            if b.get("date") == brief.date:
                briefs[i] = brief.to_dict()
                logger.info("更新已有简报: date=%s", brief.date)
                break
        else:
            briefs.append(brief.to_dict())

        data["briefs"] = briefs
        self._write_data(data)

    def get_brief(self, date: str) -> Optional[BriefReport]:
        """按日期获取简报

        Args:
            date: 日期 YYYY-MM-DD

        Returns:
            BriefReport 或 None
        """
        data = self._read_data()
        for b in data.get("briefs", []):
            if b.get("date") == date:
                return BriefReport.from_dict(b)
        return None

    def list_briefs(self, limit: int = 10) -> list:
        """获取历史简报列表

        Args:
            limit: 最大返回条数

        Returns:
            BriefReport 列表，按创建时间倒序
        """
        data = self._read_data()
        briefs = data.get("briefs", [])
        # 按 created_at 倒序
        briefs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return [BriefReport.from_dict(b) for b in briefs[:limit]]

    def save_prefs(self, prefs: UserPrefs) -> None:
        """保存用户偏好

        Args:
            prefs: 偏好对象
        """
        data = self._read_data()
        data["prefs"] = prefs.to_dict()
        self._write_data(data)
        logger.info("用户偏好已保存")

    def load_prefs(self) -> UserPrefs:
        """加载用户偏好

        Returns:
            UserPrefs 对象，不存在时返回默认
        """
        data = self._read_data()
        prefs_data = data.get("prefs", {})
        if not prefs_data:
            return UserPrefs.default()
        return UserPrefs.from_dict(prefs_data)
