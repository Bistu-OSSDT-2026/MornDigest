"""
settings.py — 全局配置加载器

从 .env 文件加载环境变量，并提供统一的配置访问接口。
使用方式:
    from config.settings import settings
    api_key = settings.get("QWEATHER_KEY")
    city = settings.get("DEFAULT_CITY", "北京")
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def _load_env() -> dict:
    """加载 .env 文件，返回配置字典"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    return os.environ


# 启动时加载
_load_env()


class Settings:
    """全局配置访问器"""

    def get(self, key: str, default: str = None) -> str:
        """获取配置项

        Args:
            key: 配置键名
            default: 默认值（当配置不存在时返回）

        Returns:
            配置字符串值，不存在时返回 default
        """
        return os.environ.get(key, default)

    def get_list(self, key: str, default: list = None, sep: str = ",") -> list:
        """获取逗号分隔的配置项，返回列表

        Args:
            key: 配置键名
            default: 默认列表
            sep: 分隔符

        Returns:
            字符串列表
        """
        value = self.get(key)
        if value is None:
            return default or []
        return [item.strip() for item in value.split(sep) if item.strip()]

    def get_int(self, key: str, default: int = 0) -> int:
        """获取整型配置项

        Args:
            key: 配置键名
            default: 默认整数值

        Returns:
            整数值
        """
        value = self.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """获取布尔型配置项

        Args:
            key: 配置键名
            default: 默认布尔值

        Returns:
            布尔值
        """
        value = self.get(key)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")

    def all(self) -> dict:
        """返回所有环境变量"""
        return dict(os.environ)


# 全局单例
settings = Settings()
