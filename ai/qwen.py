"""
qwen.py — 通义千问 (DashScope / Qwen) 大模型适配器

使用阿里云 DashScope SDK (dashscope) 调用。
"""

import logging
from models.weather import WeatherData
from models.news import NewsItem
from models.brief import BriefReport
from ai.base import AIModel, AModelError

logger = logging.getLogger(__name__)


class QwenBot(AIModel):
    """通义千问模型适配器

    参考文档: https://help.aliyun.com/zh/dashscope/
    """

    model_name = "qwen"
    model_display = "通义千问"

    def __init__(self):
        super().__init__()
        self._api_key = None

    def _get_api_key(self):
        """获取通义千问 API Key

        TODO: 刘���杰 — 实现 API Key 读取
        参考代码:
            from config.settings import settings
            api_key = settings.get("QWEN_KEY")
            if not api_key:
                raise AModelError("通义千问 API Key (QWEN_KEY) 未配置")
            return api_key
        """
        if self._api_key is None:
            raise AModelError("通义千问 API Key 待实现")
        return self._api_key

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
        # TODO: 刘志杰 — 实现以下内容
        # 参考代码:
        #   from dashscope import Generation
        #   api_key = self._get_api_key()
        #   prompt = self._build_prompt(weather, news)
        #   response = Generation.call(
        #       api_key=api_key,
        #       model="qwen-plus",  # 或 qwen-max / qwen-turbo
        #       messages=[{"role": "user", "content": prompt}],
        #       result_format="message",
        #   )
        #   if response.status_code != 200:
        #       raise AModelError(f"通义千问调用失败: {response.message}")
        #   raw = response.output.choices[0].message.content
        #   brief = self._parse_response(raw, weather, news)
        #   return brief

        raise AModelError(
            "通义千问模型接入待实现 "
            "(参考: https://help.aliyun.com/zh/dashscope/，使用 dashscope SDK)"
        )
