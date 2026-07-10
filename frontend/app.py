"""
app.py — Streamlit 主页面（通过 HTTP 调用 FastAPI 后端）

启动：streamlit run run.py
访问：http://localhost:8501
"""

import streamlit as st
from datetime import datetime

from config.constants import APP_NAME, APP_VERSION, DEFAULT_CITY
from frontend.api_client import get_client
from frontend.components import (
    render_header,
    render_weather_card,
    render_digest,
    render_news_list,
)


def init_session_state():
    """初始化 Streamlit session_state"""
    if "brief" not in st.session_state:
        st.session_state["brief"] = None
    if "is_generating" not in st.session_state:
        st.session_state["is_generating"] = False
    if "error_message" not in st.session_state:
        st.session_state["error_message"] = None
    if "prefs" not in st.session_state:
        st.session_state["prefs"] = None
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if "ai_models" not in st.session_state:
        st.session_state["ai_models"] = []


def load_prefs_from_api():
    """从后端 API 加载偏好"""
    client = get_client()
    result = client.get_prefs()
    if result["success"]:
        st.session_state["prefs"] = result["data"]
    else:
        st.session_state["error_message"] = f"加载偏好失败: {result['error']}"
        st.session_state["prefs"] = {
            "city": DEFAULT_CITY,
            "news_categories": ["科技", "综合"],
            "ai_model": "claude",
            "briefing_time": "08:00",
        }


def load_models_from_api():
    """从后端 API 加载 AI 模型列表"""
    client = get_client()
    result = client.list_ai_models()
    if result["success"]:
        st.session_state["ai_models"] = result["data"].get("models", [])
    else:
        st.session_state["ai_models"] = []


def load_history_from_api(limit: int = 10):
    """从后端 API 加载历史简报"""
    client = get_client()
    result = client.list_history(limit=limit)
    if result["success"]:
        st.session_state["history"] = result["data"]
    else:
        st.session_state["history"] = []


def main():
    """主页面入口"""
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="☀️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session_state()

    # 首次加载数据
    if st.session_state["prefs"] is None:
        load_prefs_from_api()
    if not st.session_state["ai_models"]:
        load_models_from_api()

    # ===== 页面标题 =====
    render_header()

    # ===== 侧边栏：偏好设置 =====
    render_sidebar_with_api()

    # ===== 主区域 =====
    render_main_content()

    # ===== 系统状态 =====
    render_system_status()


def render_sidebar_with_api():
    """侧边栏 - 通过 API 加载和保存偏好"""
    st.sidebar.header("⚙️ 偏好设置")

    prefs = st.session_state["prefs"]
    models = st.session_state["ai_models"]

    # 城市输入
    city = st.sidebar.text_input(
        "🏙 城市",
        value=prefs.get("city", DEFAULT_CITY),
        key="sidebar_city",
    )

    # AI 模型选择（从 API 动态加载）
    if models:
        model_options = [m["name"] for m in models]
        model_display = [m["display"] for m in models]
        current_model = prefs.get("ai_model", "claude")
        if current_model not in model_options:
            current_model = model_options[0]

        selected_display = st.sidebar.selectbox(
            "🤖 AI 模型",
            options=model_display,
            index=model_options.index(current_model),
            key="sidebar_model",
        )
        selected_model = model_options[model_display.index(selected_display)]
    else:
        selected_model = st.sidebar.text_input("🤖 AI 模型", value=prefs.get("ai_model", "claude"))

    # 新闻分类
    from config.constants import NEWS_CATEGORIES
    selected_categories = st.sidebar.multiselect(
        "📰 新闻分类",
        options=NEWS_CATEGORIES,
        default=prefs.get("news_categories", ["科技", "综合"]),
        key="sidebar_categories",
    )

    st.sidebar.markdown("---")

    # 保存按钮
    if st.sidebar.button("💾 保存偏好", type="primary", use_container_width=True):
        client = get_client()
        result = client.save_prefs(
            city=city,
            ai_model=selected_model,
            news_categories=selected_categories if selected_categories else ["综合"],
            briefing_time=prefs.get("briefing_time", "08:00"),
        )
        if result["success"]:
            st.session_state["prefs"] = result["data"]
            st.sidebar.success("✅ 已保存")
        else:
            st.sidebar.error(f"❌ 保存失败: {result['error']}")

    # 恢复默认按钮
    if st.sidebar.button("↩️ 恢复默认", use_container_width=True):
        client = get_client()
        result = client.reset_prefs()
        if result["success"]:
            st.session_state["prefs"] = result["data"]
            st.sidebar.success("✅ 已恢复默认")
            st.rerun()
        else:
            st.sidebar.error(f"❌ 失败: {result['error']}")

    # 存储到 session 以便主页使用
    st.session_state["current_city"] = city
    st.session_state["current_model"] = selected_model
    st.session_state["current_categories"] = selected_categories if selected_categories else ["综合"]

    # ===== 简报时间（只读展示） =====
    st.sidebar.markdown("---")
    st.sidebar.caption(f"⏰ 推送时间: {prefs.get('briefing_time', '08:00')}")


def render_main_content():
    """主区域内容"""
    # ===== 生成按钮 =====
    cols = st.columns([1, 1, 2])
    with cols[0]:
        generate_btn = st.button("🚀 生成今日简报", type="primary", use_container_width=True)
    with cols[1]:
        refresh_btn = st.button("🔄 刷新历史", use_container_width=True)
    with cols[2]:
        history_limit = st.selectbox("历史条数", [5, 10, 20], index=1, label_visibility="collapsed")

    if refresh_btn:
        load_history_from_api(limit=history_limit)

    if generate_btn:
        generate_brief_via_api()

    # ===== 错误提示 =====
    if st.session_state.get("error_message"):
        st.error(f"❌ {st.session_state['error_message']}")
        with st.expander("📋 错误详情"):
            st.code(st.session_state["error_message"], language="text")
        if st.button("清除错误"):
            st.session_state["error_message"] = None
            st.rerun()

    # ===== 当前简报 =====
    brief = st.session_state.get("brief")
    if brief:
        st.markdown("---")
        render_weather_card(brief.get("weather_summary", ""))
        render_digest(brief.get("digest", ""))

        news_items = brief.get("news_items", [])
        if news_items:
            st.markdown("---")
            render_news_list(news_items)

        st.markdown("---")
        cols = st.columns([1, 1, 2])
        with cols[0]:
            st.caption(f"🏙 {brief.get('city', '')}")
        with cols[1]:
            st.caption(f"🤖 {brief.get('model_used', '')}")
        with cols[2]:
            st.caption(f"生成时间：{brief.get('created_at', '')}")

        # 导出按钮
        if st.button(f"📥 导出 {brief.get('date', '')} 的简报"):
            export_url = f"http://127.0.0.1:8000/api/brief/export/{brief.get('date', '')}"
            st.markdown(f"[点击下载 Markdown 文件]({export_url})")
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
3. 等待后端 API 处理（约 3-10 秒）
4. 查看天气、简报和新闻内容

> 数据通过 FastAPI 后端处理，访问 http://localhost:8000/docs 查看 API
            """)
        with cols[1]:
            st.info("""
### 📋 当前后端状态

- **前端**: Streamlit（本页面）
- **后端**: FastAPI @ :8000
- **数据库**: JSON / SQLite
- **AI 模型**: Claude / DeepSeek / 智谱AI / 通义千问
            """)

    # ===== 历史简报 =====
    render_history_section()


def generate_brief_via_api():
    """通过 API 生成简报"""
    st.session_state["is_generating"] = True
    st.session_state["error_message"] = None

    client = get_client()

    with st.spinner("⏳ 正在生成您的晨间简报，请稍候..."):
        result = client.generate_brief(
            city=st.session_state.get("current_city"),
            model=st.session_state.get("current_model"),
            categories=st.session_state.get("current_categories"),
            news_limit=5,
            use_stored_prefs=False,
        )

    st.session_state["is_generating"] = False

    if result["success"]:
        st.session_state["brief"] = result["data"]
        # 同时刷新历史
        load_history_from_api()
        st.success("✅ 简报生成成功！")
    else:
        st.session_state["error_message"] = result["error"]
        st.rerun()


def render_history_section():
    """历史简报列表"""
    st.markdown("---")
    st.subheader("📚 历史简报")

    history = st.session_state.get("history", [])

    if not history:
        if st.button("📥 加载历史"):
            load_history_from_api()
            st.rerun()
        st.caption("暂无历史简报")
        return

    # 显示历史列表（每行3个）
    cols_per_row = 3
    for i in range(0, len(history), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(history):
                brief = history[i + j]
                with col:
                    with st.container():
                        st.markdown(f"""
                        <div style="
                            background: #f8f9fa;
                            padding: 1rem;
                            border-radius: 8px;
                            border-left: 4px solid #667eea;
                            margin-bottom: 0.5rem;
                        ">
                            <strong>📅 {brief.get('date', '')}</strong><br>
                            🏙 {brief.get('city', '')} · 🤖 {brief.get('model_used', '')}<br>
                            <small style="color:#888;">{brief.get('weather_summary', '')[:60]}...</small>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"查看", key=f"view_{brief.get('date', '')}_{i+j}"):
                            client = get_client()
                            result = client.get_brief(brief.get("date", ""))
                            if result["success"]:
                                st.session_state["brief"] = result["data"]
                                st.rerun()


def render_system_status():
    """渲染系统状态"""
    st.markdown("---")
    with st.expander("🔧 系统状态 & API 文档", expanded=False):
        client = get_client()
        health = client.health()
        if health["success"]:
            data = health["data"]
            st.success(f"""
**✅ 后端运行正常**

- **版本**: {data.get('version', '?')}
- **存储后端**: {data.get('storage_backend', '?')}
- **可用 AI 模型**: {', '.join(data.get('ai_models_available', [])) or '无'}

📖 **API 文档**: http://127.0.0.1:8000/docs
            """)
        else:
            st.error(f"❌ 后端连接失败: {health['error']}")
            st.warning("请先启动后端：`uvicorn backend.main:app --port 8000`")

        # 模型列表
        if st.session_state["ai_models"]:
            st.markdown("**AI 模型列表：**")
            for m in st.session_state["ai_models"]:
                icon = "✅" if m.get("available") else "⚠️"
                st.caption(f"{icon} **{m['display']}** ({m['name']})")


if __name__ == "__main__":
    main()
