"""
settings.py — Streamlit 设置页面

完整的用户偏好配置页：城市、新闻分类、AI 模型、简报时间等。
保存后自动写入存储模块。

实现方：芦泓天
"""

import streamlit as st

from config.constants import CITIES, NEWS_CATEGORIES, AI_MODELS
from models.prefs import UserPrefs
from storage import create_storage


st.set_page_config(
    page_title="设置 - MornDigest",
    page_icon="⚙️",
    layout="wide",
)


st.title("⚙️ 偏好设置")
st.caption("修改后点击底部保存按钮，设置将自动持久化。")
st.markdown("---")


# 加载已有偏好
storage = create_storage()
prefs = storage.load_prefs()

# ===== 城市选择 =====
st.subheader("🏙 城市")
selected_city = st.selectbox(
    "选择查看天气的城市",
    options=CITIES,
    index=CITIES.index(prefs.city) if prefs.city in CITIES else 0,
    key="city_select",
)
custom_city = st.text_input(
    "自定义城市（如不在列表中）",
    value=prefs.city if prefs.city not in CITIES else "",
    key="custom_city",
)
final_city = custom_city.strip() if custom_city.strip() else selected_city

# ===== 新闻分类 =====
st.subheader("📰 新闻分类")
selected_categories = st.multiselect(
    "选择感兴趣的新闻分类",
    options=NEWS_CATEGORIES,
    default=prefs.news_categories,
    key="categories_select",
)
if not selected_categories:
    st.warning("请至少选择一个新闻分类")
    selected_categories = ["综合"]

# ===== AI 模型选择 =====
st.subheader("🤖 AI 模型")
model_options = list(AI_MODELS.keys())
model_display = [AI_MODELS[m] for m in model_options]
model_index = model_options.index(prefs.ai_model) if prefs.ai_model in model_options else 0

selected_model_display = st.radio(
    "选择生成简报的 AI 模型",
    options=model_display,
    index=model_index,
    horizontal=True,
    key="model_select",
)
selected_model_key = model_options[model_display.index(selected_model_display)]

# ===== 简报时间 =====
st.subheader("⏰ 简报时间")
briefing_time = st.time_input(
    "定时生成简报时间",
    value=prefs.briefing_time,
    key="briefing_time",
)

# ===== 保存按钮 =====
st.markdown("---")
cols = st.columns([1, 1, 2])

with cols[0]:
    if st.button("💾 保存设置", type="primary", use_container_width=True):
        new_prefs = UserPrefs(
            city=final_city,
            news_categories=selected_categories,
            ai_model=selected_model_key,
            briefing_time=briefing_time.strftime("%H:%M") if briefing_time else "08:00",
        )
        storage.save_prefs(new_prefs)
        st.success("✅ 设置已保存！")

with cols[1]:
    if st.button("🔄 恢复默认", use_container_width=True):
        default_prefs = UserPrefs.default()
        storage.save_prefs(default_prefs)
        st.success("✅ 已恢复默认设置！")
        st.rerun()

# ===== 当前设置预览 =====
st.markdown("---")
st.subheader("📋 当前已保存设置")

saved_prefs = storage.load_prefs()
st.json(saved_prefs.to_dict(), expanded=False)

# ===== 关于 =====
with st.expander("ℹ️ 关于"):
    st.write("""
- **MornDigest v0.1.0** — AI晨间智能简报工具
- 数据存储由 `STORAGE_BACKEND` 环境变量切换（JSON / SQLite）
- API Key 配置在 `.env` 文件中
- 项目仓库：https://github.com/Bistu-OSSDT-2026/MornDigest
    """)
