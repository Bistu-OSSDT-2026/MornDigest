"""
ai — AI 大模型调用模块

提供统一的 AIModel 基类和三个模型适配器。
"""
from ai.base import AIModel, AModelError
from ai.deepseek import DeepSeekBot
from ai.zhipu import ZhipuBot
from ai.qwen import QwenBot

__all__ = ["AIModel", "AModelError", "DeepSeekBot", "ZhipuBot", "QwenBot"]
