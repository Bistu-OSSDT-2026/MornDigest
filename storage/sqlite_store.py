"""
sqlite_store.py — SQLite 数据库存储实现

使用 SQLite 数据库（data/store.db）存储简报和用户偏好。
适合需要结构化查询和更大数据量的场景。

实现方：崔锦崧
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from models.brief import BriefReport
from models.news import NewsItem
from models.prefs import UserPrefs
from storage.base import Storage, StorageError

logger = logging.getLogger(__name__)

# 数据库文件路径
DATA_DIR = Path(__file__).parent.parent / "data"
DB_FILE = DATA_DIR / "store.db"


class SqliteStore(Storage):
    """SQLite 数据库存储后端"""

    def __init__(self, db_path: str = None):
        """初始化

        Args:
            db_path: 自定义数据库路径，默认 data/store.db
        """
        self.db_path = Path(db_path) if db_path else DB_FILE
        self._ensure_dir()
        self._init_db()

    def _ensure_dir(self):
        """确保数据目录存在"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接

        Returns:
            sqlite3 连接对象
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """初始化数据库表结构

        建表 SQL：
            - briefs 表：存储历史简报
            - prefs 表：存储用户偏好（key-value）
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS briefs (
                date             TEXT NOT NULL,
                city             TEXT NOT NULL,
                weather_summary  TEXT,
                news_items       TEXT,
                digest           TEXT NOT NULL,
                model_used       TEXT DEFAULT 'deepseek',
                created_at       TEXT NOT NULL,
                PRIMARY KEY (date)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prefs (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()
        logger.info("SQLite 数据库初始化完成: %s", self.db_path)

    def save_brief(self, brief: BriefReport) -> None:
        """保存简报

        Args:
            brief: 简报对象
        """
        d = brief.to_dict()
        news_json = json.dumps(d["news_items"], ensure_ascii=False)

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO briefs
                (date, city, weather_summary, news_items, digest, model_used, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            d["date"],
            d["city"],
            d["weather_summary"],
            news_json,
            d["digest"],
            d["model_used"],
            d["created_at"],
        ))
        conn.commit()
        conn.close()
        logger.info("简报已保存 (SQLite): date=%s", brief.date)

    def get_brief(self, date: str) -> Optional[BriefReport]:
        """按日期获取简报

        Args:
            date: 日期 YYYY-MM-DD

        Returns:
            BriefReport 或 None
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM briefs WHERE date = ?", (date,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        d = dict(row)
        # 反序列化新闻列表
        try:
            d["news_items"] = json.loads(d["news_items"]) if d["news_items"] else []
        except json.JSONDecodeError:
            d["news_items"] = []

        return BriefReport.from_dict(d)

    def list_briefs(self, limit: int = 10) -> list:
        """获取历史简报列表

        Args:
            limit: 最大返回条数

        Returns:
            BriefReport 列表，按创建时间倒序
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM briefs ORDER BY created_at DESC LIMIT ?", (limit,)
        )
        rows = cursor.fetchall()
        conn.close()

        briefs = []
        for row in rows:
            d = dict(row)
            try:
                d["news_items"] = json.loads(d["news_items"]) if d["news_items"] else []
            except json.JSONDecodeError:
                d["news_items"] = []
            briefs.append(BriefReport.from_dict(d))

        return briefs

    def save_prefs(self, prefs: UserPrefs) -> None:
        """保存用户偏好

        Args:
            prefs: 偏好对象
        """
        d = prefs.to_dict()
        conn = self._get_connection()
        cursor = conn.cursor()
        for key, value in d.items():
            # 列表存为 JSON 字符串
            if isinstance(value, list):
                value = json.dumps(value, ensure_ascii=False)
            cursor.execute(
                "INSERT OR REPLACE INTO prefs (key, value) VALUES (?, ?)",
                (key, value),
            )
        conn.commit()
        conn.close()
        logger.info("用户偏好已保存 (SQLite)")

    def load_prefs(self) -> UserPrefs:
        """加载用户偏好

        Returns:
            UserPrefs 对象，不存在时返回默认
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM prefs")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return UserPrefs.default()

        d = {}
        for row in rows:
            key = row["key"]
            value = row["value"]
            # 尝试反序列化 JSON
            try:
                value = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                pass
            d[key] = value

        return UserPrefs.from_dict(d)
