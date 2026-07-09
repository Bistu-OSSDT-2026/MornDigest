"""
qwen.py — 通义千问 (DashScope / Qwen) 大模型适配器

使用阿里云 DashScope SDK (dashscope) 调用。
兼容阿里云百炼（Bailian）平台 API Key。
"""

import logging
import re
from datetime import datetime

import dashscope
from dashscope import Generation

from models.weather import WeatherData
from models.news import NewsItem
from models.brief import BriefReport
from ai.base import AIModel, AModelError
from config.settings import settings

logger = logging.getLogger(__name__)

_QWEN_MODEL = "qwen-plus"

# 与 DeepSeek / 智谱共用的段落切分规则
_SECTION_SPLIT_RE = re.compile(
    r"(?:^|\n)\s*(?:【?简报正文】?|2[\.、]?\s*简报正文|\*{0,2}简报正文\*{0,2})[:：]?\s*",
    re.IGNORECASE,
)
_WEATHER_SECTION_RE = re.compile(
    r"(?:^|\n)\s*(?:【?天气摘要】?|1[\.、]?\s*天气摘要|\*{0,2}天气摘要\*{0,2})[:：]?",
    re.IGNORECASE,
)


class QwenBot(AIModel):
    """通义千问模型适配器

    参考文档: https://help.aliyun.com/zh/dashscope/
    百炼平台: https://bailian.console.aliyun.com/
    """

    model_name = "qwen"
    model_display = "通义千问"

    def __init__(self):
        super().__init__()
        self._api_key = None

    def _get_api_key(self):
        """获取通义千问 API Key（懒加载并设置到 dashscope 全局）

        支持阿里云百炼（Bailian）平台 API Key。
        """
        if self._api_key is None:
            api_key = settings.get("QWEN_KEY")
            if not api_key:
                raise AModelError("通义千问 API Key (QWEN_KEY) 未配置")
            self._api_key = api_key
            # dashscope 也支持从全局读取，这里显式设置更稳妥
            dashscope.api_key = api_key
        return self._api_key

    def _parse_response(self, raw_response: str, weather: "WeatherData", news: "list") -> "BriefReport":
        """把模型返回的纯文本切成天气摘要 + 简报正文两段。"""
        if not raw_response or not raw_response.strip():
            raise AModelError("通义千问 返回内容为空")

        text = raw_response.strip()
        split_match = _SECTION_SPLIT_RE.search(text)
        if split_match:
            head = text[: split_match.start()].strip()
            tail = text[split_match.end():].strip()
            weather_summary = _WEATHER_SECTION_RE.sub("", head).strip(" ：:。\n")
            digest = tail or head
        else:
            parts = re.split(r"\n\s*\n", text, maxsplit=1)
            weather_summary = parts[0].strip()
            digest = parts[1].strip() if len(parts) > 1 else ""

        if not weather_summary:
            weather_summary = text[:120]
        if not digest:
            digest = text

        brief = BriefReport()
        brief.date = weather.date or datetime.now().strftime("%Y-%m-%d")
        brief.city = weather.city
        brief.weather_summary = weather_summary
        brief.digest = digest
        brief.news_items = list(news) if news else []
        brief.model_used = self.model_name
        brief.created_at = datetime.now()
        return brief

    def generate_brief(
        self,
        weather: WeatherData,
        news: list,
    ) -> BriefReport:
        """调用通义千问生成晨间简报

        Args:
            weather: 标准化天气数据
            news: 标准化新闻条目列表

        Returns:
            BriefReport: AI 生成的简报

        Raises:
            AModelError: 当 API Key 未配置或调用失败时抛出
        """
        api_key = self._get_api_key()
        prompt = self._build_prompt(weather, news)

        try:
            response = Generation.call(
                api_key=api_key,
                model=_QWEN_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000,
                result_format="message",
                timeout=60,
            )
        except Exception as e:  # dashscope 网络/SDK 异常
            raise AModelError(f"通义千问 调用异常: {e}") from e

        # DashScope 的响应对象没有 raise，需要手动检查 status_code
        if getattr(response, "status_code", 0) != 200:
            code = getattr(response, "code", "unknown")
            msg = getattr(response, "message", "未知错误")
            raise AModelError(f"通义千问 接口错误 (code={code}): {msg}")

        try:
            raw = response.output.choices[0].message.content or ""
        except (AttributeError, IndexError, KeyError) as e:
            raise AModelError(f"通义千问 返回结构异常: {e}") from e

        if not raw.strip():
            raise AModelError("通义千问 返回内容为空字符串")

        logger.info("通义千问 响应长度: %d 字符", len(raw))
        return self._parse_response(raw, weather, news)