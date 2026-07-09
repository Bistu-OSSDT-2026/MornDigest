"""
zhipu.py — 智谱AI (BigModel) 大模型适配器

使用智谱AI 官方 SDK (zhipuai>=2.0.0) 调用。
"""

import logging
import re
from datetime import datetime

from zhipuai import ZhipuAI
from zhipuai.core._errors import (
    APIStatusError,
    APITimeoutError,
    APIConnectionError,
    APIAuthenticationError,
    ZhipuAIError,
)

from models.weather import WeatherData
from models.news import NewsItem
from models.brief import BriefReport
from ai.base import AIModel, AModelError
from config.settings import settings

logger = logging.getLogger(__name__)

_ZHIPU_MODEL = "glm-4-flash"  # 速度快且免费额度充足，适合简报生成

# 与 DeepSeek 共用的段落切分规则
_SECTION_SPLIT_RE = re.compile(
    r"(?:^|\n)\s*(?:【?简报正文】?|2[\.、]?\s*简报正文|\*{0,2}简报正文\*{0,2})[:：]?\s*",
    re.IGNORECASE,
)
_WEATHER_SECTION_RE = re.compile(
    r"(?:^|\n)\s*(?:【?天气摘要】?|1[\.、]?\s*天气摘要|\*{0,2}天气摘要\*{0,2})[:：]?",
    re.IGNORECASE,
)


class ZhipuBot(AIModel):
    """智谱AI 大模型适配器

    参考文档: https://open.bigmodel.cn/dev/api
    """

    model_name = "zhipu"
    model_display = "智谱AI"

    def __init__(self):
        super().__init__()
        self._client = None

    def _get_client(self):
        """获取智谱AI API 客户端（懒加载）"""
        if self._client is None:
            api_key = settings.get("ZHIPU_KEY")
            if not api_key:
                raise AModelError("智谱AI API Key (ZHIPU_KEY) 未配置")
            try:
                self._client = ZhipuAI(api_key=api_key)
            except Exception as e:
                raise AModelError(f"智谱AI 客户端初始化失败: {e}") from e
        return self._client

    def _parse_response(self, raw_response: str, weather: "WeatherData", news: "list") -> "BriefReport":
        """把模型返回的纯文本切成天气摘要 + 简报正文两段。"""
        if not raw_response or not raw_response.strip():
            raise AModelError("智谱AI 返回内容为空")

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
        """调用智谱AI 生成晨间简报

        Args:
            weather: 标准化天气数据
            news: 标准化新闻条目列表

        Returns:
            BriefReport: AI 生成的简报

        Raises:
            AModelError: 当 API Key 未配置或调用失败时抛出
        """
        client = self._get_client()
        prompt = self._build_prompt(weather, news)

        try:
            response = client.chat.completions.create(
                model=_ZHIPU_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000,
                timeout=60,
            )
        except APIAuthenticationError as e:
            raise AModelError(f"智谱AI 鉴权失败，请检查 ZHIPU_KEY 是否正确: {e}") from e
        except APITimeoutError as e:
            raise AModelError(f"智谱AI 调用超时: {e}") from e
        except APIConnectionError as e:
            raise AModelError(f"智谱AI 网络连接失败: {e}") from e
        except APIStatusError as e:
            raise AModelError(f"智谱AI 接口错误: {e}") from e
        except ZhipuAIError as e:
            raise AModelError(f"智谱AI SDK 异常: {e}") from e
        except Exception as e:
            raise AModelError(f"智谱AI 调用出现未预期异常: {e}") from e

        if not getattr(response, "choices", None):
            raise AModelError("智谱AI 返回结果为空 choices")

        raw = response.choices[0].message.content or ""
        if not raw.strip():
            raise AModelError("智谱AI 返回内容为空字符串")

        logger.info("智谱AI 响应长度: %d 字符", len(raw))
        return self._parse_response(raw, weather, news)