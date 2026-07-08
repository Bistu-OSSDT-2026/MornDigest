"""
app.py — Streamlit 主页面

晨间简报生成与展示主入口。
用户可以设置城市/模型、一键生成简报、查看结果。

实现方：芦泓天
"""

import streamlit as st
from datetime import datetime

from config.settings import settings
from config.constants import APP_NAME, APP_VERSION, DEFAULT_CITY
from frontend.components import (
    render_header,
    render_sidebar,
    render_weather_card,
    render_digest,
    render_news_list,
    render_loading,
    render_error,
    render_success,
)
from services.brief_service import generate_morning_brief
from models.prefs import UserPrefs
from storage import create_storage


def init_session_state():
    """初始化 Streamlit session_state"""
    if "brief" not in st.session_state:
        st.session_state["brief"] = None
    if "is_generating" not in st.session_state:
        st.session_state["is_generating"] = False
    if "error_message" not in st.session_state:
        st.session_state["error_message"] = None


def main():
    """主页面入口"""
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="☀️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session_state()

    # ===== 页面标题 =====
    render_header()

    # ===== 侧边栏：快捷配置 =====
    config = render_sidebar()

    # ===== 生成按钮 =====
    cols = st.columns([1, 1, 2])
    with cols[0]:
        if st.button("🚀 生成今日简报", type="primary", use_container_width=True):
            st.session_state["is_generating"] = True
            st.session_state["error_message"] = None
            st.rerun()

    with cols[1]:
        if st.button("↩️ 刷新", use_container_width=True):
            st.session_state["brief"] = None
            st.session_state["error_message"] = None
            st.rerun()

    # ===== 执行生成 & 加载状态 =====
    if st.session_state["is_generating"]:
        try:
            with st.spinner("⏳ 正在生成您的晨间简报，请稍候..."):
                prefs = UserPrefs(
                    city=config["city"],
                    news_categories=config["categories"],
                    ai_model=config["model"],
                )
                brief = generate_morning_brief(prefs=prefs)
                st.session_state["brief"] = brief
                st.session_state["is_generating"] = False
                st.rerun()
        except Exception as e:
            st.session_state["is_generating"] = False
            st.session_state["error_message"] = str(e)
            st.rerun()

    # ===== 错误提示 =====
    if st.session_state.get("error_message"):
        render_error(st.session_state["error_message"])
        with st.expander("📋 错误详情"):
            st.code(st.session_state["error_message"], language="text")
        return

    # ===== 简报展示 =====
    brief = st.session_state.get("brief")

    if brief:
        st.markdown("---")

        # 天气摘要
        render_weather_card(brief.weather_summary)

        # AI 简报正文
        render_digest(brief.digest)

        # 新闻列表
        if brief.news_items:
            st.markdown("---")
            render_news_list(brief.news_items)

        # 底部信息
        st.markdown("---")
        cols = st.columns([1, 1, 2])
        with cols[0]:
            st.caption(f"🏙 {brief.city}")
        with cols[1]:
            st.caption(f"🤖 {brief.model_used}")
        with cols[2]:
            st.caption(f"生成时间：{brief.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        # 首次访问提示
        st.markdown("---")

        cols = st.columns([1, 1])
        with cols[0]:
            st.info("""
### 🌅 MornDigest — 晨间智能简报

**使用方式：**

1. 在左侧侧边栏设置城市和 AI 模型
2. 点击 **"生成今日简报"** 按钮
3. 等待 AI 处理（约 3-10 秒）
4. 查看天气、简报和新闻内容

> 需要配置 API Key 才能正常生成简报。
            """)
        with cols[1]:
            st.info("""
### 📋 简明功能

- **天气**：和风天气实时数据 + 预报
- **新闻**：按分类聚合最新资讯
- **AI 简报**：DeepSeek / 智谱AI / 通义千问 三选一
- **历史查询**：自动生成并保存历史简报
- **偏好设置**：保存个人城市、模型、分类偏好
            """)

        # 检查配置状态
        check_config_status()


def check_config_status():
    """检查并提示 API 配置状态"""
    st.markdown("---")
    st.subheader("🔧 配置状态")

    checks = [
        ("和风天气 API Key", "QWEATHER_KEY"),
        ("新闻 API Key", "NEWS_KEY"),
        ("DeepSeek API Key", "DEEPSEEK_KEY"),
        ("智谱AI API Key", "ZHIPU_KEY"),
        ("通义千问 API Key", "QWEN_KEY"),
    ]

    for label, key in checks:
        value = settings.get(key)
        if value:
            st.success(f"✅ {label} 已配置")
        else:
            st.warning(f"⚠️ {label} 未配置 — 请在 `.env` 中设置 `{key}`")

    backend = settings.get("STORAGE_BACKEND", "json")
    st.info(f"📦 存储后端：{backend}")


if __name__ == "__main__":
    main()
