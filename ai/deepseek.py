"""
deepseek.py — DeepSeek 大模型适配器

DeepSeek API 兼容 OpenAI 接口协议，使用 openai Python SDK 调用。
"""

import logging
import re
from datetime import datetime

from openai import OpenAI, APIError, APIConnectionError, APITimeoutError, AuthenticationError

from models.weather import WeatherData
from models.news import NewsItem
from models.brief import BriefReport
from ai.base import AIModel, AModelError
from config.settings import settings

logger = logging.getLogger(__name__)

_DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
_DEEPSEEK_MODEL = "deepseek-chat"

# 用于把模型返回文本切成「天气摘要 + 简报正文」两段
_SECTION_SPLIT_RE = re.compile(
    r"(?:^|\n)\s*(?:【?简报正文】?|2[\.、]?\s*简报正文|\*{0,2}简报正文\*{0,2})[:：]?\s*",
    re.IGNORECASE,
)
_WEATHER_SECTION_RE = re.compile(
    r"(?:^|\n)\s*(?:【?天气摘要】?|1[\.、]?\s*天气摘要|\*{0,2}天气摘要\*{0,2})[:：]?",
    re.IGNORECASE,
)


class DeepSeekBot(AIModel):
    """DeepSeek 模型适配器

    参考文档: https://api-docs.deepseek.com/
    """

    model_name = "deepseek"
    model_display = "DeepSeek"

    def __init__(self):
        super().__init__()
        self._client = None

    def _get_client(self):
        """获取 DeepSeek API 客户端（懒加载）"""
        if self._client is None:
            api_key = settings.get("DEEPSEEK_KEY")
            if not api_key:
                raise AModelError("DeepSeek API Key (DEEPSEEK_KEY) 未配置")
            try:
                self._client = OpenAI(
                    api_key=api_key,
                    base_url=_DEEPSEEK_BASE_URL,
                    timeout=60,
                )
            except Exception as e:
                raise AModelError(f"DeepSeek 客户端初始化失败: {e}") from e
        return self._client

    def _parse_response(self, raw_response: str, weather: "WeatherData", news: "list") -> "BriefReport":
        """把模型返回的纯文本切成天气摘要 + 简报正文两段。

        策略：
            1. 找到「简报正文」标题位置，前一段是天气摘要，从该标题之后到结尾是正文；
            2. 若没找到标题，回退到「按空行分两段」。
        """
        if not raw_response or not raw_response.strip():
            raise AModelError("DeepSeek 返回内容为空")

        text = raw_response.strip()
        split_match = _SECTION_SPLIT_RE.search(text)
        if split_match:
            head = text[: split_match.start()].strip()
            tail = text[split_match.end():].strip()
            # 头部再去掉「天气摘要」小标题前缀
            weather_summary = _WEATHER_SECTION_RE.sub("", head).strip(" ：:。\n")
            digest = tail or head
        else:
            # 按第一个空行切分
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
        """调用 DeepSeek 生成晨间简报

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
                model=_DEEPSEEK_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000,
                timeout=60,
            )
        except AuthenticationError as e:
            raise AModelError(f"DeepSeek 鉴权失败，请检查 DEEPSEEK_KEY 是否正确: {e}") from e
        except APITimeoutError as e:
            raise AModelError(f"DeepSeek 调用超时: {e}") from e
        except APIConnectionError as e:
            raise AModelError(f"DeepSeek 网络连接失败: {e}") from e
        except APIError as e:
            raise AModelError(f"DeepSeek 接口错误: {e}") from e
        except Exception as e:
            raise AModelError(f"DeepSeek 调用出现未预期异常: {e}") from e

        if not response.choices:
            raise AModelError("DeepSeek 返回结果为空 choices")

        raw = response.choices[0].message.content or ""
        if not raw.strip():
            raise AModelError("DeepSeek 返回内容为空字符串")

        logger.info("DeepSeek 响应长度: %d 字符", len(raw))
        return self._parse_response(raw, weather, news)