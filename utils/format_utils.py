"""
format_utils.py — 文本格式化工具

提供文本截断、空值处理、Markdown 转 Streamlit 格式等工具。
"""

import re
from typing import Optional


def truncate(text: str = None, max_length: int = 200, suffix: str = "…") -> str:
    """截断文本到指定长度

    Args:
        text: 原始文本
        max_length: 最大字符数
        suffix: 截断后缀

    Returns:
        截断后的文本
    """
    if text is None:
        return ""
    text = str(text)
    if len(text) <= max_length:
        return text
    return text[:max_length] + suffix


def empty_to_default(value: Optional[str], default: str = "暂无数据") -> str:
    """空值替换为默认文本

    Args:
        value: 原始值
        default: 默认替换文本

    Returns:
        非空文本
    """
    if value is None or str(value).strip() == "":
        return default
    return str(value).strip()


def clean_empty_lines(text: str, max_empty: int = 1) -> str:
    """清理文本中的连续空行

    Args:
        text: 原始文本
        max_empty: 最大允许连续空行数

    Returns:
        清理后的文本
    """
    if not text:
        return ""
    lines = text.split("\n")
    result = []
    empty_count = 0
    for line in lines:
        if line.strip() == "":
            empty_count += 1
            if empty_count <= max_empty:
                result.append(line)
        else:
            empty_count = 0
            result.append(line)
    return "\n".join(result)


def markdown_to_plain(md_text: str) -> str:
    """简单 Markdown 转纯文本

    去除基本 Markdown 标记（加粗、标题、列表等）。

    Args:
        md_text: Markdown 格式文本

    Returns:
        纯文本
    """
    if not md_text:
        return ""
    text = md_text
    # 去掉标题标记
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    # 去掉加粗标记
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    # 去掉斜体标记
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    # 去掉链接，只保留文本
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    # 去掉图片标记
    text = re.sub(r"!\[(.+?)\]\(.+?\)", "", text)
    # 去掉无序列表标记
    text = re.sub(r"^[*\-+]\s+", "", text, flags=re.MULTILINE)
    # 去掉分隔线
    text = re.sub(r"^-{3,}$", "", text, flags=re.MULTILINE)
    return text.strip()


def wrap_text(text: str, line_length: int = 40) -> str:
    """按指定长度简单换行

    Args:
        text: 原始文本
        line_length: 每行最大字符数

    Returns:
        换行后的文本
    """
    if not text:
        return ""
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= line_length:
            current = current + " " + word if current else word
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return "\n".join(lines)
