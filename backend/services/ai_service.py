"""
ai_service.py — AI 服务层

封装简报生成逻辑，支持多种 AI 模型：
    - claude (Anthropic)
    - deepseek (OpenAI 兼容)
    - zhipu (智谱)
    - qwen (通义千问)

复用 ai/base.py 的提示词模板和 models/brief.py 的数据结构。
"""

import logging
from datetime import datetime
from typing import List, Optional

from models.weather import WeatherData
from models.news import NewsItem
from models.brief import BriefReport
from ai.base import AIModel
from backend.services.anthropic_adapter import get_claude_service

logger = logging.getLogger(__name__)


class ClaudeBriefAdapter(AIModel):
    """Claude 适配器，继承 AIModel 基类，复用提示词模板"""

    model_name = "claude"
    model_display = "Claude (Anthropic)"

    def __init__(self):
        super().__init__()
        self._service = get_claude_service()

    def generate_brief(self, weather: WeatherData, news: list) -> BriefReport:
        prompt = self._build_prompt(weather, news)

        try:
            raw = self._service.chat(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7,
            )
            return self._parse_response(raw, weather, news)
        except RuntimeError:
            # Claude 不可用时降级返回基础简报
            logger.warning("Claude 不可用，返回降级简报")
            return _build_fallback_brief(weather, news, self.model_name)


def _build_fallback_brief(weather: WeatherData, news: list, model_name: str) -> BriefReport:
    """降级简报：AI 不可用时使用模板生成"""
    news_text = ""
    for i, item in enumerate(news[:3], 1):
        news_text += f"{i}. {item.title}\n"

    weather_summary = weather.summary_text() if weather else "天气信息获取失败"
    digest = f"""## 今日天气
{weather_summary}

## 今日要闻
{news_text if news_text else "暂无新闻"}

（简报由降级模式生成，AI 模型暂不可用）
"""

    return BriefReport(
        date=datetime.now().strftime("%Y-%m-%d"),
        city=weather.city if weather else "未知",
        weather_summary=weather_summary,
        news_items=news,
        digest=digest,
        model_used=f"{model_name} (fallback)",
        created_at=datetime.now(),
    )


def generate_brief_with_model(
    model_name: str,
    weather: WeatherData,
    news: List[NewsItem],
) -> BriefReport:
    """根据模型名生成简报

    Args:
        model_name: claude / deepseek / zhipu / qwen
        weather: 天气数据
        news: 新闻列表

    Returns:
        BriefReport
    """
    if model_name == "claude":
        bot = ClaudeBriefAdapter()
        return bot.generate_brief(weather, news)

    # 其他模型复用原有服务
    from services.brief_service import get_ai_bot
    try:
        bot = get_ai_bot(model_name)
        return bot.generate_brief(weather, news)
    except Exception as e:
        logger.error("AI 模型 %s 调用失败: %s", model_name, str(e))
        return _build_fallback_brief(weather, news, model_name)


def get_available_models() -> List[dict]:
    """获取可用的 AI 模型列表"""
    models = [
        {"name": "claude", "display": "Claude (Anthropic)",
         "available": get_claude_service().is_available},
        {"name": "deepseek", "display": "DeepSeek", "available": False},  # 需配置 DEEPSEEK_KEY
        {"name": "zhipu", "display": "智谱AI", "available": False},      # 需配置 ZHIPU_KEY
        {"name": "qwen", "display": "通义千问", "available": False},      # 需配置 QWEN_KEY
    ]
    return models
