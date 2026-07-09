"""
anthropic_adapter.py — Anthropic Claude 适配器

适配 settings.json 中的代理配置：
    ANTHROPIC_BASE_URL=https://api.minimaxi.com/anthropic
    ANTHROPIC_API_KEY=sk-cp-...
    ANTHROPIC_MODEL=MiniMax-M3

可同时作为 ai/ 模块的新适配器，让前端可通过"claude"模型选项调用 Claude。
"""

import os
import logging
from typing import List, Optional

from anthropic import Anthropic, APIError, APIConnectionError, APITimeoutError

logger = logging.getLogger(__name__)


class ClaudeService:
    """Claude API 调用服务"""

    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        base_url = os.environ.get("ANTHROPIC_BASE_URL")
        model = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

        if not api_key:
            logger.warning("ANTHROPIC_API_KEY 未配置，Claude 服务不可用")
            self._client = None
        else:
            # 使用 settings.json 中提供的 base_url（支持代理）
            client_kwargs = {"api_key": api_key}
            if base_url:
                client_kwargs["base_url"] = base_url
                logger.info("Claude 客户端使用自定义 base_url: %s", base_url)

            self._client = Anthropic(**client_kwargs)
            logger.info("Claude 客户端初始化成功")

        self._default_model = model

    @property
    def is_available(self) -> bool:
        return self._client is not None

    @property
    def model_name(self) -> str:
        return self._default_model

    def chat(
        self,
        messages: List[dict],
        system: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        model: Optional[str] = None,
    ) -> str:
        """调用 Claude API 进行对话

        Args:
            messages: [{"role": "user", "content": "..."}, ...]
            system: 系统提示词
            max_tokens: 最大输出 token
            temperature: 温度
            model: 覆盖默认模型

        Returns:
            AI 返回的文本内容

        Raises:
            RuntimeError: 当服务不可用或调用失败时
        """
        if not self.is_available:
            raise RuntimeError("Claude 服务不可用：请检查 ANTHROPIC_API_KEY 配置")

        use_model = model or self._default_model

        try:
            kwargs = {
                "model": use_model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages,
            }
            if system:
                kwargs["system"] = system

            logger.info("调用 Claude: model=%s, messages=%d", use_model, len(messages))
            response = self._client.messages.create(**kwargs)

            # 提取返回内容
            if response.content and len(response.content) > 0:
                text = response.content[0].text
                logger.info("Claude 调用成功: tokens=%s",
                            getattr(response.usage, "output_tokens", "?"))
                return text
            return ""

        except APIError as e:
            logger.error("Claude API 错误: %s", str(e))
            raise RuntimeError(f"Claude API 调用失败: {e}")
        except APIConnectionError as e:
            logger.error("Claude 连接错误: %s", str(e))
            raise RuntimeError(f"无法连接到 Claude API: {e}")
        except APITimeoutError as e:
            logger.error("Claude 调用超时: %s", str(e))
            raise RuntimeError(f"Claude API 调用超时: {e}")
        except Exception as e:
            logger.error("Claude 未知错误: %s", str(e))
            raise RuntimeError(f"Claude 调用异常: {e}")


# 全局单例
_claude_service: Optional[ClaudeService] = None


def get_claude_service() -> ClaudeService:
    """获取 Claude 服务单例"""
    global _claude_service
    if _claude_service is None:
        _claude_service = ClaudeService()
    return _claude_service
