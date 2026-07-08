"""
zhipu.py — 智谱AI (BigModel) 大模型适配器

使用智谱AI 官方 SDK (zhipuai) 调用。
"""

import logging
from models.weather import WeatherData
from models.news import NewsItem
from models.brief import BriefReport
from ai.base import AIModel, AModelError

logger = logging.getLogger(__name__)


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
        """获取智谱AI API 客户端

        TODO: 刘志杰 — 实现客户端初始化
        参考代码:
            from zhipuai import ZhipuAI
            from config.settings import settings

            api_key = settings.get("ZHIPU_KEY")
            if not api_key:
                raise AModelError("智谱AI API Key (ZHIPU_KEY) 未配置")

            return ZhipuAI(api_key=api_key)
        """
        if self._client is None:
            # TODO: 刘志杰 — 初始化智谱AI 客户端
            raise AModelError("智谱AI 客户端待实现")
        return self._client

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
        # TODO: 刘志杰 — 实现以下内容
        # 1. 获取客户端: client = self._get_client()
        # 2. 组装提示词: prompt = self._build_prompt(weather, news)
        # 3. 调用 API:
        #    response = client.chat.completions.create(
        #        model="glm-4",  # 或实际模型名 glm-4-plus / glm-4-flash
        #        messages=[{"role": "user", "content": prompt}],
        #        temperature=0.7,
        #    )
        # 4. 获取返回内容: raw = response.choices[0].message.content
        # 5. 解析返回: brief = self._parse_response(raw, weather, news)
        # 6. 返回: return brief

        raise AModelError(
            "智谱AI 模型接入待实现 "
            "(参考: https://open.bigmodel.cn/dev/api，使用 zhipuai SDK)"
        )
