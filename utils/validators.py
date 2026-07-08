"""
validators.py — 数据验证工具

提供城市名、参数范围、模型名等验证函数。
"""

from typing import Optional

from config.constants import CITIES, NEWS_CATEGORIES, AI_MODELS

# CITIES_ALLOW_CUSTOM = True 表示允许输入不在预设列表中的城市
CITIES_ALLOW_CUSTOM = True


def validate_city(city: str) -> str:
    """验证城市名

    Args:
        city: 城市名

    Returns:
        标准化后的城市名

    Raises:
        ValueError: 城市名为空时抛出
    """
    if not city or not city.strip():
        raise ValueError("城市名不能为空")

    city = city.strip()

    if not CITIES_ALLOW_CUSTOM:
        # 严格模式：必须在预设城市列表中
        matched = [c for c in CITIES if c == city]
        if not matched:
            raise ValueError(
                f"不支持的城市: {city}，可选: {'、'.join(CITIES[:10])} 等"
            )

    return city


def validate_model(model_name: str) -> str:
    """验证 AI 模型名

    Args:
        model_name: 模型标识

    Returns:
        标准化的模型名 (小写)

    Raises:
        ValueError: 模型名不合法时抛出
    """
    if not model_name:
        raise ValueError("模型名不能为空")

    model_name = model_name.strip().lower()

    if model_name not in AI_MODELS:
        options = ", ".join(AI_MODELS.keys())
        raise ValueError(f"不支持的 AI 模型: {model_name}，可选: {options}")

    return model_name


def validate_categories(categories: list) -> list:
    """验证新闻分类列表

    Args:
        categories: 分类名称列表

    Returns:
        过滤后的合法分类列表

    Raises:
        ValueError: 列表为空且无默认值时抛出
    """
    if not categories:
        raise ValueError("新闻分类列表不能为空")

    valid = []
    for cat in categories:
        cat = str(cat).strip()
        if cat in NEWS_CATEGORIES:
            valid.append(cat)

    if not valid:
        options = "、".join(NEWS_CATEGORIES)
        raise ValueError(f"没有合法的新闻分类，可选: {options}")

    return valid


def validate_positive_int(value: int, max_value: int = 1000, field_name: str = "值") -> int:
    """验证正整数

    Args:
        value: 待验证的整数
        max_value: 最大允许值
        field_name: 字段名（用于错误提示）

    Returns:
        验证后的整数值

    Raises:
        ValueError: 值不合法时抛出
    """
    try:
        v = int(value)
    except (ValueError, TypeError):
        raise ValueError(f"{field_name}必须是整数")

    if v <= 0:
        raise ValueError(f"{field_name}必须为正整数")

    if v > max_value:
        raise ValueError(f"{field_name}不能超过 {max_value}")

    return v


def validate_time_range(time_str: str) -> str:
    """验证时间格式 HH:MM

    Args:
        time_str: 时间字符串

    Returns:
        标准化后的时间字符串

    Raises:
        ValueError: 格式不合法时抛出
    """
    if not time_str:
        raise ValueError("时间不能为空")

    parts = str(time_str).strip().split(":")
    if len(parts) != 2:
        raise ValueError("时间格式应为 HH:MM，如 08:00")

    try:
        h, m = int(parts[0]), int(parts[1])
    except ValueError:
        raise ValueError("时间格式应为 HH:MM，如 08:00")

    if h < 0 or h > 23:
        raise ValueError("小时范围: 0-23")
    if m < 0 or m > 59:
        raise ValueError("分钟范围: 0-59")

    return f"{h:02d}:{m:02d}"
