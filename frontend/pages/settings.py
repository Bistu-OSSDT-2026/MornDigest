"""
settings.py — Streamlit 设置页面（通过 HTTP 调用 FastAPI 后端）
"""

import streamlit as st

from config.constants import CITIES, NEWS_CATEGORIES, AI_MODELS
from frontend.api_client import get_client


st.set_page_config(
    page_title="设置 - MornDigest",
    page_icon="⚙️",
    layout="wide",
)


st.title("⚙️ 偏好设置")
st.caption("修改后点击底部保存按钮，设置将通过 API 保存到后端存储")
st.markdown("---")


def load_prefs():
    """从后端 API 加载偏好"""
    client = get_client()
    result = client.get_prefs()
    if result["success"]:
        return result["data"]
    st.error(f"加载偏好失败: {result['error']}")
    return None


def load_models():
    """从后端 API 加载模型列表"""
    client = get_client()
    result = client.list_ai_models()
    if result["success"]:
        return result["data"].get("models", [])
    return []


# 加载数据
prefs = load_prefs()
models = load_models()

if prefs is None:
    st.stop()


# ===== 城市选择 =====
st.subheader("🏙 城市")
selected_city = st.selectbox(
    "选择查看天气的城市",
    options=CITIES,
    index=CITIES.index(prefs.get("city", "北京")) if prefs.get("city") in CITIES else 0,
    key="city_select",
)
custom_city = st.text_input(
    "自定义城市（如不在列表中）",
    value=prefs.get("city", "") if prefs.get("city") not in CITIES else "",
    key="custom_city",
)
final_city = custom_city.strip() if custom_city.strip() else selected_city

# ===== 新闻分类 =====
st.subheader("📰 新闻分类")
selected_categories = st.multiselect(
    "选择感兴趣的新闻分类",
    options=NEWS_CATEGORIES,
    default=prefs.get("news_categories", ["科技", "综合"]),
    key="categories_select",
)
if not selected_categories:
    st.warning("请至少选择一个新闻分类")
    selected_categories = ["综合"]

# ===== AI 模型选择 =====
st.subheader("🤖 AI 模型")
if models:
    model_options = [m["name"] for m in models]
    model_display = [m["display"] for m in models]
    current = prefs.get("ai_model", "claude")
    if current not in model_options:
        current = model_options[0]

    selected_display = st.radio(
        "选择生成简报的 AI 模型",
        options=model_display,
        index=model_options.index(current),
        horizontal=True,
        key="model_select",
    )
    selected_model_key = model_options[model_display.index(selected_display)]

    # 显示可用性
    for m in models:
        icon = "✅" if m["available"] else "⚠️ 未配置"
        if m["name"] == selected_model_key:
            st.caption(f"已选: {icon} **{m['display']}**")
else:
    selected_model_key = st.text_input("AI 模型标识", value=prefs.get("ai_model", "claude"))

# ===== 简报时间 =====
st.subheader("⏰ 简报时间")
briefing_time_str = prefs.get("briefing_time", "08:00")
try:
    from datetime import datetime
    default_time = datetime.strptime(briefing_time_str, "%H:%M").time()
except Exception:
    default_time = datetime.strptime("08:00", "%H:%M").time()

briefing_time = st.time_input(
    "定时生成简报时间",
    value=default_time,
    key="briefing_time",
)

# ===== 保存按钮 =====
st.markdown("---")
cols = st.columns([1, 1, 2])

with cols[0]:
    if st.button("💾 保存设置", type="primary", use_container_width=True):
        client = get_client()
        result = client.save_prefs(
            city=final_city,
            ai_model=selected_model_key,
            news_categories=selected_categories,
            briefing_time=briefing_time.strftime("%H:%M"),
        )
        if result["success"]:
            st.success("✅ 设置已保存！")
        else:
            st.error(f"❌ 保存失败: {result['error']}")

with cols[1]:
    if st.button("🔄 恢复默认", use_container_width=True):
        client = get_client()
        result = client.reset_prefs()
        if result["success"]:
            st.success("✅ 已恢复默认设置！")
            st.rerun()
        else:
            st.error(f"❌ 失败: {result['error']}")

# ===== 当前设置预览 =====
st.markdown("---")
st.subheader("📋 当前已保存设置")

fresh_prefs = load_prefs()
if fresh_prefs:
    st.json(fresh_prefs, expanded=False)

# ===== 关于 =====
with st.expander("ℹ️ 关于"):
    st.write("""
- **MornDigest v0.1.0** — AI晨间智能简报工具
- **前端**: Streamlit
- **后端**: FastAPI @ http://127.0.0.1:8000
- **数据存储**: 由 `STORAGE_BACKEND` 环境变量切换（JSON / SQLite）
- **API Key 配置**: 在 `.env` 文件中
- **API 文档**: http://127.0.0.1:8000/docs
- **项目仓库**: https://github.com/Bistu-OSSDT-2026/MornDigest
    """)
