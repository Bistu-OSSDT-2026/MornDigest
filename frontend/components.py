"""
components.py — Streamlit 可复用 UI 组件

适配 FastAPI 后端返回的 dict 格式数据。
"""

import streamlit as st
from utils.format_utils import empty_to_default


def render_weather_card(weather_summary: str = None):
    """渲染天气卡片

    Args:
        weather_summary: 天气摘要文本
    """
    weather_text = empty_to_default(weather_summary, "天气信息加载中...")

    with st.container():
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
            margin: 0.5rem 0;
        ">
            <h3 style="margin: 0; font-size: 1.1rem; opacity: 0.9;">🌤 今日天气</h3>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"> {weather_text}")
        st.markdown("---")


def render_news_card(item: dict) -> None:
    """渲染单条新闻卡片（接受 dict 格式）

    Args:
        item: dict 或 NewsItem 对象，包含 title/summary/source/url/publish_time/category
    """
    # 兼容 dict 和对象两种格式
    def _get(key, default=""):
        if isinstance(item, dict):
            return item.get(key, default)
        return getattr(item, key, default)

    title = _get("title")
    if not title:
        return

    with st.container():
        st.markdown(f"### 📰 {title}")
        cols = st.columns([3, 1])
        with cols[0]:
            st.caption(f"来源：{empty_to_default(_get('source'))}")
        with cols[1]:
            st.caption(f"分类：{empty_to_default(_get('category', '综合'))}")

        publish_time = _get("publish_time", "")
        if publish_time:
            st.caption(f"🕒 {publish_time}")

        summary = _get("summary", "")
        if summary:
            st.write(summary)
        url = _get("url", "")
        if url:
            st.markdown(f"[🔗 阅读原文]({url})")
        st.markdown("---")


def render_news_list(news_items: list) -> None:
    """渲染新闻列表

    Args:
        news_items: NewsItem 列表或 dict 列表
    """
    if not news_items:
        st.info("📭 暂无新闻内容")
        return

    st.markdown("### 📰 今日要闻")
    for item in news_items:
        render_news_card(item)


def render_digest(digest: str = None):
    """渲染 AI 简报正文

    Args:
        digest: AI 生成的简报正文
    """
    digest_text = empty_to_default(digest, "简报内容加载中...")

    with st.container():
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
            margin: 0.5rem 0;
        ">
            <h3 style="margin: 0; font-size: 1.1rem; opacity: 0.9;">✨ 智能简报</h3>
        </div>
        """, unsafe_allow_html=True)

        st.write(digest_text)


def render_loading():
    """渲染加载动画"""
    st.spinner("⏳ 正在生成您的晨间简报...")


def render_error(message: str = "生成简报时发生错误"):
    """渲染错误提示"""
    st.error(f"❌ {message}")


def render_info(message: str):
    """渲染信息提示"""
    st.info(f"💡 {message}")


def render_success(message: str):
    """渲染成功提示"""
    st.success(f"✅ {message}")


def render_header():
    """渲染页面顶部标题栏"""
    from utils.date_utils import today_with_weekday

    st.markdown("""
        <style>
        .stTitle p { font-size: 2rem; }
        </style>
    """, unsafe_allow_html=True)

    st.title("☀️ MornDigest — 晨间智能简报")

    cols = st.columns([3, 1, 3])
    with cols[1]:
        st.caption(today_with_weekday())


def render_sidebar():
    """侧边栏（保留旧接口，向后兼容）

    Returns:
        dict: {"city": str, "model": str, "categories": list[str]}
    """
    from config.constants import AI_MODELS, NEWS_CATEGORIES, DEFAULT_CITY, DEFAULT_MODEL

    st.sidebar.header("⚙️ 快捷设置")

    city = st.sidebar.text_input("🏙 城市", value=DEFAULT_CITY)

    model_options = ["deepseek", "zhipu", "qwen", "claude"]
    model_display_names = [AI_MODELS.get(m, m.upper()) for m in model_options]
    default_idx = model_options.index(DEFAULT_MODEL) if DEFAULT_MODEL in model_options else 0

    selected_index = st.sidebar.selectbox(
        "🤖 AI 模型",
        options=model_display_names,
        index=default_idx,
        format_func=lambda x: x,
    )
    selected_model_key = model_options[model_display_names.index(selected_index)]

    selected_categories = st.sidebar.multiselect(
        "📰 新闻分类",
        options=NEWS_CATEGORIES,
        default=["科技", "综合"],
    )

    return {
        "city": city.strip() if city.strip() else DEFAULT_CITY,
        "model": selected_model_key,
        "categories": selected_categories if selected_categories else ["科技", "综合"],
    }
