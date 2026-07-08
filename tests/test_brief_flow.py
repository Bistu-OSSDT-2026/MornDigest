"""
test_brief_flow.py — 简报生成流程测试骨架

测试覆盖：
  1. 数据模型序列化/反序列化
  2. 配置加载
  3. 工具函数
  4. 存储读写（骨架，需联网环境时跳过 API 测试）

运行方式:
    pytest tests/
    pytest tests/test_brief_flow.py -v
"""

import pytest
from datetime import datetime

# ---- 数据模型测试 ----


def test_weather_data_to_dict():
    """测试 WeatherData 序列化"""
    from models.weather import WeatherData

    w = WeatherData(
        city="北京",
        date="2026-07-08",
        temp_now=25.0,
        condition="晴",
        humidity=45,
        wind_level="3级",
        forecast=["明天: 晴 18-26°"],
    )
    d = w.to_dict()

    assert d["city"] == "北京"
    assert d["temp_now"] == 25.0
    assert d["condition"] == "晴"
    assert d["forecast"] == ["明天: 晴 18-26°"]
    assert isinstance(d["timestamp"], str)


def test_weather_data_from_dict():
    """测试 WeatherData 反序列化"""
    from models.weather import WeatherData

    d = {
        "city": "上海",
        "date": "2026-07-09",
        "temp_now": 30.0,
        "temp_min": 26.0,
        "temp_max": 33.0,
        "condition": "多云",
        "humidity": 70,
        "wind_level": "2级",
        "forecast": [],
        "source": "qweather",
        "timestamp": "2026-07-09T08:00:00",
    }
    w = WeatherData.from_dict(d)

    assert w.city == "上海"
    assert w.condition == "多云"
    assert isinstance(w.timestamp, datetime)


def test_news_item_serialization():
    """测试 NewsItem 序列化/反序列化"""
    from models.news import NewsItem

    item = NewsItem(
        title="测试标题",
        summary="测试摘要",
        source="测试媒体",
        category="科技",
        url="https://example.com",
        publish_time="2026-07-08 08:00",
    )
    d = item.to_dict()
    restored = NewsItem.from_dict(d)

    assert restored.title == "测试标题"
    assert restored.category == "科技"


def test_brief_report_with_news():
    """测试 BriefReport 含嵌套 NewsItem 的序列化"""
    from models.brief import BriefReport
    from models.news import NewsItem

    brief = BriefReport(
        date="2026-07-08",
        city="北京",
        weather_summary="今天晴天",
        news_items=[
            NewsItem(title="新闻1", summary="摘要1", source="媒体A"),
            NewsItem(title="新闻2", summary="摘要2", source="媒体B"),
        ],
        digest="这是简报正文",
        model_used="deepseek",
    )
    d = brief.to_dict()

    assert d["city"] == "北京"
    assert len(d["news_items"]) == 2
    assert d["news_items"][0]["title"] == "新闻1"

    # 反序列化测试
    restored = BriefReport.from_dict(d)
    assert len(restored.news_items) == 2
    assert restored.news_items[0].title == "新闻1"


def test_user_prefs_default():
    """测试 UserPrefs 默认值"""
    from models.prefs import UserPrefs

    prefs = UserPrefs.default()
    assert prefs.city == "北京"
    assert prefs.ai_model == "deepseek"
    assert "科技" in prefs.news_categories


# ---- 配置测试 ----


def test_settings_get():
    """测试配置读取"""
    from config.settings import settings

    # 测试有默认值的读取
    city = settings.get("DEFAULT_CITY", "北京")
    assert city is not None  # .env 存在时返回实际值，否则返回默认


def test_constants_exist():
    """测试常量模块可导入"""
    from config.constants import (
        CITIES,
        NEWS_CATEGORIES,
        AI_MODELS,
        DEFAULT_CITY,
        DEFAULT_MODEL,
    )

    assert DEFAULT_CITY == "北京"
    assert DEFAULT_MODEL == "deepseek"
    assert "北京" in CITIES
    assert "科技" in NEWS_CATEGORIES
    assert "deepseek" in AI_MODELS


# ---- 工具函数测试 ----


def test_validate_city():
    """测试城市名验证"""
    from utils.validators import validate_city

    assert validate_city("北京") == "北京"
    assert validate_city(" 上海 ") == "上海"

    with pytest.raises(ValueError):
        validate_city("")


def test_validate_model():
    """测试模型名验证"""
    from utils.validators import validate_model

    assert validate_model("deepseek") == "deepseek"
    assert validate_model("ZHIPU") == "zhipu"

    with pytest.raises(ValueError):
        validate_model("unknown_model")


def test_validate_categories():
    """测试分类验证"""
    from utils.validators import validate_categories

    result = validate_categories(["科技", "综合"])
    assert "科技" in result
    assert "综合" in result

    with pytest.raises(ValueError):
        validate_categories([])


def test_truncate():
    """测试文本截断"""
    from utils.format_utils import truncate

    assert truncate("Hello", max_length=10) == "Hello"
    assert truncate("Hello World", max_length=5) == "Hello…"


def test_date_utils():
    """测试日期工具"""
    from utils.date_utils import today, today_with_weekday

    assert len(today()) == 10  # YYYY-MM-DD
    assert "星期" in today_with_weekday()


# ---- AI 基类测试 ----


def test_ai_model_raises():
    """测试 AIModel 基类正确抛出异常"""
    from ai.base import AIModel
    from models.weather import WeatherData

    class TestBot(AIModel):
        model_name = "test"
        model_display = "Test"

        def generate_brief(self, weather, news):
            raise NotImplementedError("待实现")

    bot = TestBot()
    with pytest.raises(NotImplementedError):
        bot.generate_brief(WeatherData(), [])


# ---- 适配骨架测试（仅测试可实例化） ----


def test_deepseek_bot_instantiable():
    """测试 DeepSeekBot 可实例化"""
    from ai.deepseek import DeepSeekBot

    bot = DeepSeekBot()
    assert bot.model_name == "deepseek"


def test_zhipu_bot_instantiable():
    """测试 ZhipuBot 可实例化"""
    from ai.zhipu import ZhipuBot

    bot = ZhipuBot()
    assert bot.model_name == "zhipu"


def test_qwen_bot_instantiable():
    """测试 QwenBot 可实例化"""
    from ai.qwen import QwenBot

    bot = QwenBot()
    assert bot.model_name == "qwen"
