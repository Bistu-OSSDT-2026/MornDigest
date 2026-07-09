"""
test_storage.py — storage 模块专项测试

测试覆盖:
    1. SqliteStore (8 个): 初始化、CRUD、覆盖、默认回退
    2. JsonStore  (3 个): CRUD、覆盖
    3. Factory    (2 个): 默认 json、env 切换 sqlite

所有测试使用 pytest 的 tmp_path fixture 隔离数据目录,不会触碰
项目根目录下的 data/store.db 或 data/store.json。

运行方式:
    pytest tests/test_storage.py -v
    pytest tests/ -v
"""

import pytest
from datetime import datetime


# ============================================================
# SqliteStore 测试 (8 个)
# ============================================================


def test_sqlite_init_creates_db_file(tmp_path):
    """构造 SqliteStore 后,数据库文件应自动创建"""
    from storage.sqlite_store import SqliteStore

    db_path = tmp_path / "test.db"
    SqliteStore(db_path=str(db_path))

    assert db_path.exists()
    assert db_path.stat().st_size > 0


def test_sqlite_init_creates_parent_dir(tmp_path):
    """传入深层路径,父目录应被自动创建"""
    from storage.sqlite_store import SqliteStore

    nested = tmp_path / "a" / "b" / "c" / "store.db"
    SqliteStore(db_path=str(nested))

    assert nested.exists()
    assert nested.parent.is_dir()


def test_sqlite_save_then_get_brief(tmp_path):
    """BriefReport 应能完整往返 (含嵌套 NewsItem)"""
    from storage.sqlite_store import SqliteStore
    from models.brief import BriefReport
    from models.news import NewsItem

    store = SqliteStore(db_path=str(tmp_path / "t.db"))
    brief = BriefReport(
        date="2026-07-09",
        city="北京",
        weather_summary="今天北京晴",
        news_items=[
            NewsItem(title="新闻1", summary="摘要1", source="媒体A", category="科技"),
            NewsItem(title="新闻2", summary="摘要2", source="媒体B", category="综合"),
        ],
        digest="完整简报正文",
        model_used="deepseek",
    )

    store.save_brief(brief)
    loaded = store.get_brief("2026-07-09")

    assert loaded is not None
    assert loaded.date == "2026-07-09"
    assert loaded.city == "北京"
    assert loaded.weather_summary == "今天北京晴"
    assert loaded.digest == "完整简报正文"
    assert loaded.model_used == "deepseek"
    assert len(loaded.news_items) == 2
    assert loaded.news_items[0].title == "新闻1"
    assert loaded.news_items[1].category == "综合"


def test_sqlite_save_brief_overwrites_same_date(tmp_path):
    """同日期二次保存应覆盖更新 (PK upsert)"""
    from storage.sqlite_store import SqliteStore
    from models.brief import BriefReport

    store = SqliteStore(db_path=str(tmp_path / "t.db"))
    brief_a = BriefReport(
        date="2026-07-09", city="北京", weather_summary="A",
        digest="A版", model_used="deepseek",
    )
    brief_b = BriefReport(
        date="2026-07-09", city="北京", weather_summary="B",
        digest="B版", model_used="zhipu",
    )

    store.save_brief(brief_a)
    store.save_brief(brief_b)

    loaded = store.get_brief("2026-07-09")
    assert loaded is not None
    assert loaded.weather_summary == "B"
    assert loaded.digest == "B版"
    assert loaded.model_used == "zhipu"


def test_sqlite_get_brief_returns_none_for_missing_date(tmp_path):
    """不存在的日期应返回 None 而不是抛异常"""
    from storage.sqlite_store import SqliteStore

    store = SqliteStore(db_path=str(tmp_path / "t.db"))
    result = store.get_brief("1999-01-01")

    assert result is None


def test_sqlite_list_briefs_orders_by_created_at_desc(tmp_path):
    """list_briefs 应按 created_at 倒序返回 (最新在前)"""
    from storage.sqlite_store import SqliteStore
    from models.brief import BriefReport

    store = SqliteStore(db_path=str(tmp_path / "t.db"))
    store.save_brief(BriefReport(
        date="2026-07-07", city="北京", weather_summary="",
        digest="最早", model_used="deepseek",
        created_at=datetime(2026, 7, 7, 8, 0, 0),
    ))
    store.save_brief(BriefReport(
        date="2026-07-09", city="北京", weather_summary="",
        digest="最新", model_used="deepseek",
        created_at=datetime(2026, 7, 9, 8, 0, 0),
    ))
    store.save_brief(BriefReport(
        date="2026-07-08", city="北京", weather_summary="",
        digest="中间", model_used="deepseek",
        created_at=datetime(2026, 7, 8, 8, 0, 0),
    ))

    briefs = store.list_briefs(limit=10)

    assert len(briefs) == 3
    assert briefs[0].digest == "最新"
    assert briefs[1].digest == "中间"
    assert briefs[2].digest == "最早"


def test_sqlite_save_and_load_prefs(tmp_path):
    """UserPrefs 应能完整往返"""
    from storage.sqlite_store import SqliteStore
    from models.prefs import UserPrefs

    store = SqliteStore(db_path=str(tmp_path / "t.db"))
    prefs = UserPrefs(
        city="上海",
        news_categories=["科技", "财经"],
        ai_model="zhipu",
        briefing_time="09:30",
    )

    store.save_prefs(prefs)
    loaded = store.load_prefs()

    assert loaded.city == "上海"
    assert loaded.news_categories == ["科技", "财经"]
    assert loaded.ai_model == "zhipu"
    assert loaded.briefing_time == "09:30"


def test_sqlite_load_prefs_returns_default_when_empty(tmp_path):
    """空库应返回 UserPrefs.default()"""
    from storage.sqlite_store import SqliteStore
    from models.prefs import UserPrefs

    store = SqliteStore(db_path=str(tmp_path / "t.db"))
    prefs = store.load_prefs()

    assert isinstance(prefs, UserPrefs)
    assert prefs.city == UserPrefs.default().city
    assert prefs.ai_model == UserPrefs.default().ai_model


# ============================================================
# JsonStore 测试 (3 个)
# ============================================================


def test_json_save_then_get_brief(tmp_path):
    """JsonStore 的 BriefReport 完整往返"""
    from storage.json_store import JsonStore
    from models.brief import BriefReport
    from models.news import NewsItem

    store = JsonStore(store_path=str(tmp_path / "t.json"))
    brief = BriefReport(
        date="2026-07-09",
        city="上海",
        weather_summary="上海多云",
        news_items=[
            NewsItem(title="新闻A", summary="内容A", source="媒体X", category="财经"),
        ],
        digest="上海简报",
        model_used="qwen",
    )

    store.save_brief(brief)
    loaded = store.get_brief("2026-07-09")

    assert loaded is not None
    assert loaded.city == "上海"
    assert loaded.digest == "上海简报"
    assert loaded.model_used == "qwen"
    assert len(loaded.news_items) == 1
    assert loaded.news_items[0].title == "新闻A"


def test_json_save_brief_overwrites_same_date(tmp_path):
    """JsonStore 同日期应覆盖更新"""
    from storage.json_store import JsonStore
    from models.brief import BriefReport

    store = JsonStore(store_path=str(tmp_path / "t.json"))
    store.save_brief(BriefReport(
        date="2026-07-09", city="北京", weather_summary="",
        digest="旧内容", model_used="deepseek",
    ))
    store.save_brief(BriefReport(
        date="2026-07-09", city="北京", weather_summary="",
        digest="新内容", model_used="deepseek",
    ))

    loaded = store.get_brief("2026-07-09")
    assert loaded is not None
    assert loaded.digest == "新内容"

    # 不应有重复条目
    all_briefs = store.list_briefs(limit=10)
    assert len(all_briefs) == 1


def test_json_save_and_load_prefs(tmp_path):
    """JsonStore 的 UserPrefs 完整往返"""
    from storage.json_store import JsonStore
    from models.prefs import UserPrefs

    store = JsonStore(store_path=str(tmp_path / "t.json"))
    prefs = UserPrefs(
        city="深圳",
        news_categories=["体育"],
        ai_model="qwen",
        briefing_time="07:00",
    )

    store.save_prefs(prefs)
    loaded = store.load_prefs()

    assert loaded.city == "深圳"
    assert loaded.news_categories == ["体育"]
    assert loaded.ai_model == "qwen"
    assert loaded.briefing_time == "07:00"


# ============================================================
# Factory 测试 (2 个)
# ============================================================


def test_create_storage_defaults_to_json(monkeypatch, tmp_path):
    """未设置 STORAGE_BACKEND 时,应返回 JsonStore"""
    from storage import create_storage
    from storage.json_store import JsonStore
    from storage import json_store as json_store_module

    # 把默认 data 目录重定向到 tmp_path,避免污染项目根目录
    monkeypatch.setattr(json_store_module, "STORE_FILE", tmp_path / "t.json")
    monkeypatch.delenv("STORAGE_BACKEND", raising=False)

    store = create_storage()
    assert isinstance(store, JsonStore)


def test_create_storage_returns_sqlite_when_env_set(monkeypatch, tmp_path):
    """设置 STORAGE_BACKEND=sqlite 时,应返回 SqliteStore"""
    from storage import create_storage
    from storage.sqlite_store import SqliteStore
    from storage import sqlite_store as sqlite_store_module

    # 把默认 db 路径重定向到 tmp_path,避免污染项目根目录
    monkeypatch.setattr(sqlite_store_module, "DB_FILE", tmp_path / "t.db")
    monkeypatch.setenv("STORAGE_BACKEND", "sqlite")

    store = create_storage()
    assert isinstance(store, SqliteStore)
