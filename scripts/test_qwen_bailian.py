"""
test_qwen_bailian.py — 真实调用阿里云百炼 Qwen-plus 验证脚本

用法：
    1. 复制 .env.example 为 .env，填入 QWEN_KEY=你的百炼 key
    2. python scripts/test_qwen_bailian.py
"""

import sys
from pathlib import Path

# 确保项目根目录在 Python 路径中
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from models.weather import WeatherData
from models.news import NewsItem
from ai.qwen import QwenBot


def main():
    weather = WeatherData(
        city="北京",
        date="2026-07-09",
        temp_now=28.0,
        temp_min=22.0,
        temp_max=33.0,
        condition="晴转多云",
        humidity=55,
        wind_level="3级",
        forecast=["明天: 多云 21-29°", "后天: 阴 20-28°"],
    )

    news = [
        NewsItem(
            title="阿里通义千问 Qwen3 正式开源",
            summary="性能比上一代提升 40%，支持 128K 上下文",
            source="量子位",
            category="科技",
        ),
        NewsItem(
            title="A 股三大指数小幅高开",
            summary="沪指开盘涨 0.3%，科技股领涨",
            source="财经网",
            category="财经",
        ),
    ]

    print("正在调用百炼 Qwen-plus 生成简报...")
    print("（首次冷启动约 3-5 秒）")
    print()

    try:
        brief = QwenBot().generate_brief(weather, news)
    except Exception as e:
        print(f"[X] 调用失败: {e}")
        sys.exit(1)

    print("=" * 60)
    print(f"[日期] {brief.date}    [城市] {brief.city}    [模型] {brief.model_used}")
    print("=" * 60)
    print()
    print("【天气摘要】")
    print(brief.weather_summary)
    print()
    print("【简报正文】")
    print(brief.digest)
    print()
    print(f"【字数统计】{brief.word_count()} 字")
    print(f"【生成时间】{brief.created_at.strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()