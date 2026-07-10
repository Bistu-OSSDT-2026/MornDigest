"""
test_ai_bots.py — AI 模型适配器单元测试

覆盖范围：
    1. Bot 类签名（必须符合 AIModel 接口契约）
    2. services.brief_service.get_ai_bot 工厂
    3. 缺失 API Key 时的异常处理
    4. 基类 _build_prompt 的渲染正确性
    5. _parse_response 的多格式解析（含 fallback）
    6. 三家 Provider 端到端 mock（deepseek / zhipu / qwen）
    7. 异常分类（鉴权 / 超时 / 连接 / 接口错误）是否被正确包装为 AModelError

运行：
    pytest tests/test_ai_bots.py -v
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch


# ============================================================
# 1. 类签名 / 模型标识
# ============================================================

def test_three_bots_have_distinct_model_names():
    """三家 Bot 必须有互不相同的 model_name。"""
    from ai.deepseek import DeepSeekBot
    from ai.zhipu import ZhipuBot
    from ai.qwen import QwenBot

    names = {DeepSeekBot().model_name, ZhipuBot().model_name, QwenBot().model_name}
    assert names == {"deepseek", "zhipu", "qwen"}


def test_three_bots_inherit_aimodel():
    """三个 Bot 都必须是 AIModel 子类。"""
    from ai.base import AIModel
    from ai.deepseek import DeepSeekBot
    from ai.zhipu import ZhipuBot
    from ai.qwen import QwenBot

    for cls in (DeepSeekBot, ZhipuBot, QwenBot):
        assert issubclass(cls, AIModel)


def test_model_display_in_chinese():
    """model_display 字段必须使用中文展示名（前端直接显示）。"""
    from ai.deepseek import DeepSeekBot
    from ai.zhipu import ZhipuBot
    from ai.qwen import QwenBot

    assert DeepSeekBot.model_display == "DeepSeek"
    assert ZhipuBot.model_display == "智谱AI"
    assert QwenBot.model_display == "通义千问"


# ============================================================
# 2. services.get_ai_bot 工厂
# ============================================================

def test_get_ai_bot_returns_correct_instance():
    """get_ai_bot 应该按名字返回正确的 Bot 实例。"""
    from ai.base import AIModel
    from ai.deepseek import DeepSeekBot
    from ai.zhipu import ZhipuBot
    from ai.qwen import QwenBot
    from services.brief_service import get_ai_bot

    assert isinstance(get_ai_bot("deepseek"), DeepSeekBot)
    assert isinstance(get_ai_bot("zhipu"), ZhipuBot)
    assert isinstance(get_ai_bot("qwen"), QwenBot)
    for name in ("deepseek", "zhipu", "qwen"):
        assert isinstance(get_ai_bot(name), AIModel)


def test_get_ai_bot_invalid_name_raises():
    """get_ai_bot 对未知模型名应抛 AModelError。"""
    from ai.base import AModelError
    from services.brief_service import get_ai_bot

    with pytest.raises(AModelError) as exc:
        get_ai_bot("gpt-4")
    assert "gpt-4" in str(exc.value)
    assert "deepseek" in str(exc.value)  # 提示可选列表


# ============================================================
# 3. 缺失 API Key 时的行为
# ============================================================

@pytest.fixture
def clean_env(monkeypatch):
    """每个测试用例都从干净环境开始，确保 key 真的没配。"""
    for k in ("DEEPSEEK_KEY", "ZHIPU_KEY", "QWEN_KEY"):
        monkeypatch.delenv(k, raising=False)
    return monkeypatch


def test_deepseek_missing_key_raises(clean_env):
    from ai.base import AModelError
    from ai.deepseek import DeepSeekBot

    with pytest.raises(AModelError) as exc:
        DeepSeekBot()._get_client()
    assert "DEEPSEEK_KEY" in str(exc.value)


def test_zhipu_missing_key_raises(clean_env):
    from ai.base import AModelError
    from ai.zhipu import ZhipuBot

    with pytest.raises(AModelError) as exc:
        ZhipuBot()._get_client()
    assert "ZHIPU_KEY" in str(exc.value)


def test_qwen_missing_key_raises(clean_env):
    from ai.base import AModelError
    from ai.qwen import QwenBot

    with pytest.raises(AModelError) as exc:
        QwenBot()._get_api_key()
    assert "QWEN_KEY" in str(exc.value)


def test_key_loaded_lazily_only_once(clean_env, monkeypatch):
    """_get_client 只在首次调用时读取 key；读取后切换 env 不应影响。"""
    from ai.deepseek import DeepSeekBot

    bot = DeepSeekBot()
    monkeypatch.setenv("DEEPSEEK_KEY", "sk-test-key")

    # 第一次调用：触发 key 读取
    with patch("ai.deepseek.OpenAI") as mock_openai:
        mock_openai.return_value = MagicMock()
        bot._get_client()
        assert mock_openai.call_args.kwargs["api_key"] == "sk-test-key"

    # 切换环境变量：已缓存 client 不应重新读取
    monkeypatch.setenv("DEEPSEEK_KEY", "sk-different-key")
    with patch("ai.deepseek.OpenAI") as mock_openai:
        bot._get_client()
        mock_openai.assert_not_called()  # 未重新初始化


# ============================================================
# 4. _build_prompt 渲染
# ============================================================

@pytest.fixture
def sample_weather():
    from models.weather import WeatherData

    return WeatherData(
        city="北京",
        date="2026-07-09",
        temp_now=25.0,
        temp_min=20.0,
        temp_max=30.0,
        condition="晴",
        humidity=45,
        wind_level="3级",
        forecast=["明天: 多云 21-29°", "后天: 阴 20-28°"],
    )


@pytest.fixture
def sample_news():
    from models.news import NewsItem

    return [
        NewsItem(title="AI 芯片新突破", summary="性能提升 30%", source="科技日报", category="科技"),
        NewsItem(title="A 股小幅高开", summary="市场情绪稳定", source="财经网", category="财经"),
    ]


def test_build_prompt_contains_weather(sample_weather):
    from ai.deepseek import DeepSeekBot

    prompt = DeepSeekBot()._build_prompt(sample_weather, [])
    assert "北京" in prompt
    assert "晴" in prompt
    assert "20" in prompt and "30" in prompt  # 温度
    assert "45" in prompt  # 湿度


def test_build_prompt_contains_news(sample_weather, sample_news):
    from ai.deepseek import DeepSeekBot

    prompt = DeepSeekBot()._build_prompt(sample_weather, sample_news)
    assert "AI 芯片新突破" in prompt
    assert "A 股小幅高开" in prompt
    assert "科技日报" in prompt
    assert "财经网" in prompt


def test_build_prompt_handles_empty_news(sample_weather):
    from ai.deepseek import DeepSeekBot

    prompt = DeepSeekBot()._build_prompt(sample_weather, [])
    assert "暂无新闻" in prompt


def test_build_prompt_contains_output_instructions(sample_weather, sample_news):
    """prompt 必须明确告诉模型要输出哪些部分（天气摘要 / 简报正文）。"""
    from ai.deepseek import DeepSeekBot

    prompt = DeepSeekBot()._build_prompt(sample_weather, sample_news)
    assert "天气摘要" in prompt
    assert "简报正文" in prompt


# ============================================================
# 5. _parse_response 解析
# ============================================================

@pytest.fixture
def sample_weather_short():
    from models.weather import WeatherData

    return WeatherData(
        city="北京",
        date="2026-07-09",
        temp_now=25.0,
        temp_min=20.0,
        temp_max=30.0,
        condition="晴",
    )


def _assert_basic_brief(brief, weather):
    """断言 BriefReport 基础字段填充正确。"""
    from models.brief import BriefReport

    assert isinstance(brief, BriefReport)
    assert brief.date == weather.date
    assert brief.city == weather.city
    assert brief.model_used == "deepseek"
    assert brief.weather_summary
    assert brief.digest


def test_parse_standard_marked_format(sample_weather_short):
    """标准格式：1. 天气摘要... 2. 简报正文... 能正确切两段。"""
    from ai.deepseek import DeepSeekBot

    raw = """1. 天气摘要：今天北京晴，气温 20-30°C，建议穿着轻薄外套。

2. 简报正文：今天天气晴朗适合户外活动。科技板块有大新闻，财经方面 A 股小幅高开。综合来看是美好的一天。"""

    brief = DeepSeekBot()._parse_response(raw, sample_weather_short, [])
    _assert_basic_brief(brief, sample_weather_short)
    assert "晴" in brief.weather_summary and "20-30" in brief.weather_summary
    assert "科技板块" in brief.digest
    # 摘要里不应包含简报正文的标记
    assert "简报正文" not in brief.weather_summary


def test_parse_plain_paragraph_format(sample_weather_short):
    """无标记时：按第一个空行切两段。"""
    from ai.deepseek import DeepSeekBot

    raw = """今天北京天气晴朗，气温 20 到 30 度，适合户外活动，建议多喝水。

科技板块今天有大新闻：AI 芯片性能提升 30%。
财经方面 A 股小幅高开。
综合来看今天是个不错的开始。"""

    brief = DeepSeekBot()._parse_response(raw, sample_weather_short, [])
    _assert_basic_brief(brief, sample_weather_short)
    assert "晴朗" in brief.weather_summary
    assert "AI 芯片" in brief.digest


def test_parse_single_paragraph_fallback(sample_weather_short):
    """只有一段（无空行）时：weather 取前 120 字，digest 取整段。"""
    from ai.deepseek import DeepSeekBot

    raw = "今天北京天气晴朗气温 20 到 30 度，适合户外活动，AI 芯片有新突破，A 股小幅高开。"
    brief = DeepSeekBot()._parse_response(raw, sample_weather_short, [])
    _assert_basic_brief(brief, sample_weather_short)
    assert brief.weather_summary  # 非空
    assert brief.digest == raw  # digest 取整段


def test_parse_empty_response_raises(sample_weather_short):
    from ai.base import AModelError
    from ai.deepseek import DeepSeekBot

    with pytest.raises(AModelError):
        DeepSeekBot()._parse_response("", sample_weather_short, [])


def test_parse_whitespace_only_raises(sample_weather_short):
    from ai.base import AModelError
    from ai.deepseek import DeepSeekBot

    with pytest.raises(AModelError):
        DeepSeekBot()._parse_response("   \n  \t  ", sample_weather_short, [])


def test_parse_preserves_news_items(sample_weather_short, sample_news):
    """传入的 news 应该原样写入 BriefReport.news_items。"""
    from ai.deepseek import DeepSeekBot

    raw = "天气摘要：晴。\n\n简报正文：科技板块有大新闻。"
    brief = DeepSeekBot()._parse_response(raw, sample_weather_short, sample_news)
    assert len(brief.news_items) == 2
    assert brief.news_items[0].title == "AI 芯片新突破"


def test_parse_sets_created_at(sample_weather_short):
    """created_at 必须有值。"""
    from datetime import datetime
    from ai.deepseek import DeepSeekBot

    raw = "天气摘要：晴。\n\n简报正文：今天不错。"
    brief = DeepSeekBot()._parse_response(raw, sample_weather_short, [])
    assert isinstance(brief.created_at, datetime)


def test_parse_falls_back_to_today_when_date_missing():
    """weather.date 为空时，brief.date 应回退到今天。"""
    from datetime import datetime
    from models.weather import WeatherData
    from ai.deepseek import DeepSeekBot

    w = WeatherData(city="北京", date="", temp_now=25.0, temp_min=20.0, temp_max=30.0, condition="晴")
    raw = "天气摘要：晴。\n\n简报正文：今天不错。"
    brief = DeepSeekBot()._parse_response(raw, w, [])
    assert brief.date == datetime.now().strftime("%Y-%m-%d")


# ============================================================
# 6. 三家 Provider 端到端 mock
# ============================================================

def _mock_chat_response(content: str):
    """构造 OpenAI 兼容格式的 chat.completions 响应。"""
    resp = MagicMock()
    resp.choices = [MagicMock()]
    resp.choices[0].message.content = content
    return resp


def _mock_qwen_response(content: str, status_code: int = 200, code: str = "", message: str = ""):
    """构造 DashScope 风格的响应对象。"""
    resp = MagicMock()
    resp.status_code = status_code
    resp.code = code
    resp.message = message
    resp.output.choices = [MagicMock()]
    resp.output.choices[0].message.content = content
    return resp


SAMPLE_AI_TEXT = """1. 天气摘要：今天北京晴朗，气温 20-30 度。

2. 简报正文：科技板块发布新一代 AI 芯片。A 股今日小幅高开。综合来看今天适合出行。"""


def test_deepseek_generate_brief_end_to_end(sample_weather_short, monkeypatch):
    """端到端：mock openai 客户端返回 → 验证 BriefReport 填充正确。"""
    from ai.deepseek import DeepSeekBot

    monkeypatch.setenv("DEEPSEEK_KEY", "sk-test")
    with patch("ai.deepseek.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = _mock_chat_response(SAMPLE_AI_TEXT)
        mock_openai_cls.return_value = mock_client

        brief = DeepSeekBot().generate_brief(sample_weather_short, [])

    assert brief.model_used == "deepseek"
    assert "晴朗" in brief.weather_summary
    assert "AI 芯片" in brief.digest
    # 验证确实调过 API
    mock_client.chat.completions.create.assert_called_once()
    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "deepseek-chat"


def test_deepseek_generate_brief_uses_settings_key(sample_weather_short, monkeypatch):
    """验证 _get_client 读的是 settings.get('DEEPSEEK_KEY')，不是 os.getenv 直读。"""
    from ai.deepseek import DeepSeekBot

    monkeypatch.setenv("DEEPSEEK_KEY", "sk-from-env")
    with patch("ai.deepseek.OpenAI") as mock_openai_cls:
        mock_openai_cls.return_value = MagicMock()
        DeepSeekBot()._get_client()
    assert mock_openai_cls.call_args.kwargs["api_key"] == "sk-from-env"


def test_zhipu_generate_brief_end_to_end(sample_weather_short, monkeypatch):
    """端到端：mock zhipuai 客户端返回。"""
    from ai.zhipu import ZhipuBot

    monkeypatch.setenv("ZHIPU_KEY", "test-zhipu-key")
    with patch("ai.zhipu.ZhipuAI") as mock_zhipu_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = _mock_chat_response(SAMPLE_AI_TEXT)
        mock_zhipu_cls.return_value = mock_client

        brief = ZhipuBot().generate_brief(sample_weather_short, [])

    assert brief.model_used == "zhipu"
    assert "AI 芯片" in brief.digest
    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert "glm-" in call_kwargs["model"]


def test_qwen_generate_brief_end_to_end(sample_weather_short, monkeypatch):
    """端到端：mock dashscope.Generation.call 返回。"""
    from ai.qwen import QwenBot

    monkeypatch.setenv("QWEN_KEY", "test-qwen-key")
    with patch("ai.qwen.Generation.call") as mock_call:
        mock_call.return_value = _mock_qwen_response(SAMPLE_AI_TEXT)

        brief = QwenBot().generate_brief(sample_weather_short, [])

    assert brief.model_used == "qwen"
    assert "AI 芯片" in brief.digest
    call_kwargs = mock_call.call_args.kwargs
    assert "qwen" in call_kwargs["model"]
    assert call_kwargs["result_format"] == "message"


# ============================================================
# 7. 异常分类
# ============================================================

def test_deepseek_authentication_error_wrapped(sample_weather_short, monkeypatch):
    """openai AuthenticationError → AModelError（提示用户检查 key）。"""
    from openai import AuthenticationError
    from ai.base import AModelError
    from ai.deepseek import DeepSeekBot

    monkeypatch.setenv("DEEPSEEK_KEY", "bad-key")
    fake_err = AuthenticationError(
        "invalid api key",
        response=MagicMock(),
        body=None,
    )

    with patch("ai.deepseek.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = fake_err
        mock_openai_cls.return_value = mock_client
        with pytest.raises(AModelError) as exc:
            DeepSeekBot().generate_brief(sample_weather_short, [])
    assert "鉴权失败" in str(exc.value) or "DEEPSEEK_KEY" in str(exc.value)


def test_deepseek_timeout_error_wrapped(sample_weather_short, monkeypatch):
    from openai import APITimeoutError
    from ai.base import AModelError
    from ai.deepseek import DeepSeekBot

    monkeypatch.setenv("DEEPSEEK_KEY", "sk-test")
    fake_err = APITimeoutError(request=MagicMock())

    with patch("ai.deepseek.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = fake_err
        mock_openai_cls.return_value = mock_client
        with pytest.raises(AModelError) as exc:
            DeepSeekBot().generate_brief(sample_weather_short, [])
    assert "超时" in str(exc.value)


def test_deepseek_connection_error_wrapped(sample_weather_short, monkeypatch):
    from openai import APIConnectionError
    from ai.base import AModelError
    from ai.deepseek import DeepSeekBot

    monkeypatch.setenv("DEEPSEEK_KEY", "sk-test")
    fake_err = APIConnectionError(request=MagicMock())

    with patch("ai.deepseek.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = fake_err
        mock_openai_cls.return_value = mock_client
        with pytest.raises(AModelError) as exc:
            DeepSeekBot().generate_brief(sample_weather_short, [])
    assert "连接" in str(exc.value) or "网络" in str(exc.value)


def test_qwen_non_200_status_raises(sample_weather_short, monkeypatch):
    """DashScope 风格：status_code != 200 必须抛 AModelError（不是 raise 是手动检查）。"""
    from ai.base import AModelError
    from ai.qwen import QwenBot

    monkeypatch.setenv("QWEN_KEY", "sk-test")
    fake_resp = _mock_qwen_response("", status_code=400, code="InvalidApiKey", message="key 无效")

    with patch("ai.qwen.Generation.call") as mock_call:
        mock_call.return_value = fake_resp
        with pytest.raises(AModelError) as exc:
            QwenBot().generate_brief(sample_weather_short, [])
    assert "InvalidApiKey" in str(exc.value) or "key" in str(exc.value).lower()


def test_qwen_empty_response_raises(sample_weather_short, monkeypatch):
    """模型返回空字符串时必须抛 AModelError，不能静默返回空 BriefReport。"""
    from ai.base import AModelError
    from ai.qwen import QwenBot

    monkeypatch.setenv("QWEN_KEY", "sk-test")
    fake_resp = _mock_qwen_response("", status_code=200)

    with patch("ai.qwen.Generation.call") as mock_call:
        mock_call.return_value = fake_resp
        with pytest.raises(AModelError):
            QwenBot().generate_brief(sample_weather_short, [])


def test_deepseek_empty_response_raises(sample_weather_short, monkeypatch):
    from ai.base import AModelError
    from ai.deepseek import DeepSeekBot

    monkeypatch.setenv("DEEPSEEK_KEY", "sk-test")
    with patch("ai.deepseek.OpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = _mock_chat_response("   \n  ")
        mock_openai_cls.return_value = mock_client
        with pytest.raises(AModelError):
            DeepSeekBot().generate_brief(sample_weather_short, [])