"""
base.py — AI 模型基类

定义所有 AI 模型适配器必须实现的统一接口。
各模型适配器继承此类，实现 generate_brief 方法。

使用方：services/brief_service.py
实现方：刘志杰
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime

from models.weather import WeatherData
from models.news import NewsItem
from models.brief import BriefReport

logger = logging.getLogger(__name__)


class AModelError(Exception):
    """AI 模型调用异常"""
    pass


class AIModel(ABC):
    """AI 模型基类

    所有模型适配器必须继承此类并实现 generate_brief 方法。

    Attributes:
        model_name: 模型标识名 (deepseek / zhipu / qwen)
        model_display: 模型显示名 (DeepSeek / 智谱AI / 通义千问)
    """

    model_name: str = ""
    model_display: str = ""

    def __init__(self):
        """初始化模型"""
        pass

    @abstractmethod
    def generate_brief(
        self,
        weather: WeatherData,
        news: list,
    ) -> BriefReport:
        """输入天气+新闻素材，经 AI 处理后输出简报

        各模型适配器必须实现此方法。

        Args:
            weather: 标准化天气数据
            news: 标准化新闻条目列表

        Returns:
            BriefReport: AI 生成的简报

        Raises:
            AModelError: 当 API Key 未配置或调用失败时抛出
        """
        raise NotImplementedError

    def _build_prompt(
        self,
        weather: WeatherData,
        news: list,
    ) -> str:
        """组装发送给 AI 的提示词

        提示词结构：
            1. 角色设定
            2. 天气数据段落
            3. 新闻数据段落
            4. 输出格式要求
            5. 语气约束

        Args:
            weather: 天气数据
            news: 新闻列表

        Returns:
            组装好的提示词字符串
        """
        weather_text = weather.summary_text()

        news_text = ""
        for i, item in enumerate(news, 1):
            news_text += f"{i}. {item.title} — {item.summary}（来源：{item.source}）\n"

        prompt = f"""你是一位专业的晨间简报助手，负责为用户生成一份简洁的晨间简报。

## 今天的信息

### 天气
{weather_text}

### 新闻素材
{news_text if news_text else "暂无新闻"}

### 未来天气
"""
        for f in weather.forecast:
            prompt += f"- {f}\n"

        prompt += """
## 请生成以下内容

1. **天气摘要**（100字以内）：用亲切自然的口吻描述今天天气，给出一句穿衣或出行建议。
2. **简报正文**（200-400字）：综合天气和新闻信息，用流畅的语言组织成一段话。
   开头提一句天气感受，然后列出 1-3 条值得关注的新闻要点（每条1-2句话），最后用一句话收尾。

## 注意事项
- 语言简洁有条理
- 使用简体中文
- 不要罗列全部新闻，只摘要最有价值的
- 不用使用 Markdown 格式，输出纯文本即可
- 语气温暖友好，像私人助理在汇报
"""
        return prompt

    def _parse_response(
        self,
        raw_response: str,
        weather: WeatherData,
        news: list,
    ) -> BriefReport:
        """解析 AI 返回的原始文本，组装为 BriefReport

        默认实现：将完整响应同时填入 weather_summary 和 digest。
        各适配器可根据实际返回格式覆盖此方法。

        Args:
            raw_response: AI 返回的原始字符串
            weather: 天气数据
            news: 新闻列表

        Returns:
            BriefReport 对象
        """
        brief = BriefReport()
        brief.date = weather.date or datetime.now().strftime("%Y-%m-%d")
        brief.city = weather.city
        brief.weather_summary = raw_response[:300] if len(raw_response) > 200 else raw_response
        brief.digest = raw_response
        brief.news_items = news
        brief.model_used = self.model_name
        brief.created_at = datetime.now()

        return brief
