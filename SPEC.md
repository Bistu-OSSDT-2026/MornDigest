# MornDigest — 产品规格与技术设计文档

> AI晨间智能简报工具
> v0.1.0 (初始版本)
> 最后更新: 2026-07-09 (崔锦崧 补全 storage 测试 + 文档同步)

---

## 📌 本版本变更日志 (2026-07-09 崔锦崧)

本人在本分支对项目做以下改动（不影响现有任何代码接口）：

| 类别 | 文件 | 改动 |
|------|------|------|
| 新增 | `tests/test_storage.py` | 13 个 storage 专项测试（SqliteStore 8 + JsonStore 3 + 工厂 2） |
| 新增 | `storage/README.md` | storage 模块使用文档 |
| 修改 | `AGENTS.md` | 团队状态 / 测试数 / 审查记录同步 |
| 修改 | `SPEC.md` | §10 路线图 Phase 2 存储模块勾选完成；附录 D 测试指南同步 |
| 修改 | `README.md` | 修复合并冲突标记 + 同步 storage 测试覆盖 |

**接口影响**：**零**。`storage/` 目录 4 个核心文件未动。

**测试结果**：`pytest tests/ -v` → 29 passed（16 流程 + 13 storage 专项）。

---

## 文档说明

本文档描述 MornDigest **做什么**、**怎么做**以及**数据如何流动**。面向后续接手开发的队员编写，目标是让每个模块负责人只看自己相关章节即可开工。

**阅读指南**：
- 了解产品全貌 → 看第 1-2 章
- 理解系统架构 → 看第 3 章
- 知道自己要实现什么 → 看对应章节(4-8)
- 理解业务流程 → 看第 5 章
- 部署运维 → 看第 9-10 章

文档结构遵循功能 → 架构 → 模块 → 流程 的顺序展开。

---

## 1. 产品概述

### 1.1 产品定位

MornDigest 是一款轻量化信息聚合网页工具，如同专属私人助理，每日晨间自动汇总天气、新闻等多源信息，经由 AI 大模型智能分析和润色，生成一份结构清晰的个性化晨间简报。

### 1.2 目标用户

日常需要快速了解天气、获取行业资讯的个人用户。通过一键生成简报，免去逐个打开天气app、新闻网站的信息碎片化体验。

### 1.3 核心价值主张

- **省时**：多源信息一次聚合，无需逐个查看
- **智能**：AI 用自然语言重新组织，不是简单罗列标题
- **个性化**：可定制城市、新闻偏好、AI 模型
- **轻量**：纯浏览器访问，无需安装

---

## 2. 功能规格

### 2.1 v0.1.0 功能清单

| ID | 功能 | 优先级 | 说明 |
|----|------|--------|------|
| F1 | 城市选择 | P0 | 用户可选查看城市天气 |
| F2 | 新闻分类筛选 | P0 | 勾选感兴趣的资讯类别（科技/财经/体育/综合） |
| F3 | AI模型切换 | P0 | 前端支持 DeepSeek/智谱AI/通义千问 三选一 |
| F4 | 一键生成简报 | P0 | 核心功能，触发完整数据拉取+AI处理流程 |
| F5 | 简报内容展示 | P0 | 天气摘要 + AI简报正文 + 新闻列表 完整渲染 |
| F6 | 偏好设置保存 | P1 | 用户修改后的设置持久化，下次打开自动恢复 |
| F7 | 历史简报查看 | P1 | 查看以往日期生成的简报记录 |
| F8 | 简报导出下载 | P1 | 将简报导出为文本文件 |

### 2.2 版本范围边界

**在本版本中**：
- [x] 多源数据采集（天气 + 新闻）
- [x] 三家 AI 大模型接入与切换
- [x] 本地数据持久化
- [x] 基础用户偏好配置
- [x] 历史简报查看与导出

**不在本版本内**：
- [ ] 多用户登录/注册体系
- [ ] 邮件/定时推送
- [ ] 移动端适配与 PWA
- [ ] 社区/分享功能

---

## 3. 系统架构

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                   Streamlit 前端 (frontend/)              │
│  ┌───────────┐  ┌───────────┐  ┌───────────────────┐    │
│  │  主页面    │  │  设置页    │  │  简报展示组件      │    │
│  └─────┬─────┘  └─────┬─────┘  └────────┬──────────┘    │
│        │               │                   │              │
│        │    UserPrefs  │    UserPrefs      │              │
└────────┼───────────────┼───────────────────┼──────────────┘
         │               │                   │
         ▼               │                   │
┌────────────────────────┤                   │
│  services/brief_service│                   │
│  (核心编排)            │                   │
│  generate_morning_brief│                   │
└────────┬───────────────┼───────────────────┘
         │               │
   ┌─────┴────┐          │         ┌────────┴──────┐
   ▼          ▼          ▼         ▼               ▼
┌────────┐ ┌──────┐ ┌────────┐ ┌─────────┐  ┌────────┐
│天气API │ │新闻  │ │  AI    │ │ 存储   │  │工具函数│
│(和风)  │ │API   │ │模型    │ │(SQLite │  │utils/  │
│        │ │      │ │        │ │/JSON)  │  │        │
└────────┘ └──────┘ └────────┘ └─────────┘  └────────┘
```

### 3.2 架构设计原则

**原则 1：模块隔离**。每个模块只在自己的目录下编写代码，跨模块协作通过 `models/` 中定义的标准数据类完成。

**原则 2：接口先行**。框架阶段已为所有模块写好调用钩子（基类 + 空函数），实现方只需在钩子内填充业务逻辑，不改入口签名。

**原则 3：配置集中**。所有外部 Key、默认参数统一由 `.env` + `config/settings.py` 管理，各模块通过 `settings.get()` 读取，不硬编码。

**原则 4：业务编排独立**。`services/brief_service.py` 唯一负责串接完整流程，其他模块只提供原子能力。

---

## 4. 模块详细设计

### 4.1 前端界面模块 (`frontend/`) — 芦泓天

#### 功能需求

**主页面 (app.py)：**
- 顶部显示标题 "MornDigest" + 日期
- 中心区域显示当前城市的当日天气概览（温度、状况、风速、湿度、未来3日）
- 一键生成简报按钮（点击后显示加载动画）
- AI 生成的简报正文区域（天气摘要 + 新闻摘要）
- 新闻列表区域（标题/摘要/来源/链接的卡片列表）
- 加载状态与错误提示（请求中/失败/超时）

**设置页 (pages/settings.py)：**
- 城市选择（下拉框或文本输入）
- 新闻分类勾选（多选框：科技、财经、体育、综合）
- AI 模型切换（单选：DeepSeek / 智谱AI / 通义千问）
- 保存按钮 → 调用存储模块写入 UserPrefs
- 页面打开时自动加载上次保存的偏好

**可复用组件 (components.py)：**
- `render_weather_card(data)` — 天气卡片样式
- `render_news_card(item)` — 新闻卡片样式
- `render_digest(text)` — 简报正文渲染
- `render_loading()` — 加载动画组件
- `render_error(msg)` — 错误提示组件

#### 技术实现

基于 Streamlit 框架构建：

```python
# frontend/app.py — Streamlit 主入口
import streamlit as st
from config.settings import settings
from services.brief_service import generate_morning_brief
from frontend.components import render_weather_card, render_news_card, render_digest, render_loading
from storage.base import Storage

st.set_page_config(page_title="MornDigest", layout="wide")
st.title("☀️ MornDigest — 晨间智能简报")

# 1. 加载用户偏好
storage = Storage()
prefs = storage.load_prefs()
default_city = prefs.city or settings.get("DEFAULT_CITY", "北京")

# 2. 侧边栏：快捷设置
with st.sidebar:
    city = st.text_input("城市", value=default_city)
    model = st.selectbox("AI模型", ["deepseek", "zhipu", "qwen"])
    st.page_link("pages/settings.py", label="完整设置")

# 3. 生成按钮
if st.button("生成今日简报"):
    with st.spinner("正在生成简报..."):
        brief = generate_morning_brief(city=city, model=model)
        st.session_state["brief"] = brief

# 4. 渲染简报
brief = st.session_state.get("brief")
if brief:
    render_weather_card(brief.weather_summary)
    render_digest(brief.digest)
    for item in brief.news_items:
        render_news_card(item)
```

#### 交互说明

| 用户操作 | 系统响应 |
|----------|----------|
| 点击"生成今日简报" | 显示加载动画 → 调用 `brief_service.generate_morning_brief()` → 渲染天气/简报/新闻 |
| 修改城市/新闻类别/模型 | 点击保存后调用 `storage.save_prefs()` 写入偏好 |
| 点击新闻标题链接 | 浏览器新标签页打开原始链接 |

#### 对接接口

```python
# 调用方：前端
from services.brief_service import generate_morning_brief
from storage.base import Storage

# 生成简报
brief = generate_morning_brief(prefs)

# 读取/保存偏好
storage = Storage()
prefs = storage.load_prefs()
storage.save_prefs(prefs)
```

---

### 4.2 天气 & 新闻数据源模块 (`api/`) — 芦泓天

#### 功能需求

**天气模块 (weather_api.py)：**
- 调用和风天气实时天气接口 (https://dev.qweather.com/docs/api/weather/weather-now/)
- 调用和风天气未来7天预报接口
- 解析原始 JSON 响应 → 组装为标准 `WeatherData` 对象返回
- 捕获并处理网络异常、API 参数错误、空数据等情况

**新闻模块 (news_api.py)：**
- 按用户选中的分类拉取新闻（类别：科技、财经、体育、综合）
- 每个分类取前 N 条（默认 5 条）
- 解析原始响应 → 转为 `NewsItem` 列表返回
- 处理跨域、超时、限流、空数据等情况

#### 技术实现

```python
# api/weather_api.py
import requests
from config.settings import settings
from models.weather import WeatherData
from datetime import datetime

def fetch_weather(city: str) -> WeatherData:
    """从和风天气API获取指定城市天气数据

    步骤：
    1. 调用地理编码接口获取 location_id
    2. 调用实时天气接口获取当前天气
    3. 调用预报接口获取未来3日数据
    4. 解析并组装为标准 WeatherData 返回
    """
    api_key = settings.get("QWEATHER_KEY")

    # 步骤 1: 获取 location_id
    geo_url = f"https://geo.qweather.com/v2/city/lookup?location={city}&key={api_key}"
    resp = requests.get(geo_url, timeout=10)
    resp.raise_for_status()
    geo_data = resp.json()
    # TODO: 解析 location_id (芦泓天填充)

    # 步骤 2: 获取实时天气
    # TODO: 调用实时天气接口 (芦泓天填充)

    # 步骤 3: 获取预报
    # TODO: 调用预报接口 (芦泓天填充)

    # 步骤 4: 组装返回
    # TODO: 组装 WeatherData 对象并返回 (芦泓天填充)
    pass


# api/news_api.py
import requests
from config.settings import settings
from models.news import NewsItem

def fetch_news(categories: list[str], limit: int = 5) -> list[NewsItem]:
    """按类别获取新闻列表

    步骤：
    1. 遍历每个分类，调用对应新闻 API
    2. 解析原始响应
    3. 转换为标准 NewsItem 对象列表
    4. 合并、去重、截断到 limit 条
    """
    api_key = settings.get("NEWS_KEY")

    all_items = []

    # TODO: 实现新闻拉取逻辑 (芦泓天填充)
    # 示例伪代码：
    # for category in categories:
    #     resp = requests.get(新闻接口url, params={"key": api_key, "cat": category, "limit": limit})
    #     items = resp.json()["articles"]
    #     for item in items:
    #         all_items.append(NewsItem(
    #             title=item["title"],
    #             summary=item["description"],
    #             source=item["source"],
    #             category=category,
    #             url=item["url"],
    #             publish_time=item["publishedAt"],
    #         ))

    return all_items[:limit]
```

#### 数据流

```
用户输入城市 ──→ weather_api.fetch_weather()
                            │
                            ├──→ 和风天气 geo 接口 (获取 location_id)
                            ├──→ 和风天气 now 接口 (实时天气)
                            └──→ 和风天气 7d 接口 (预报)
                                    │
                                    ▼
                            解析 JSON → WeatherData 对象

用户选中类别 ──→ news_api.fetch_news(categories)
                          │
                          ├──→ 新闻 API (每个类别请求)
                          │
                          ▼
                  解析响应 → list[NewsItem] → 合并 → 截断 → 返回
```

#### 对接接口

```python
# 调用方：brief_service
from api.weather_api import fetch_weather
from api.news_api import fetch_news

weather = fetch_weather(city="北京")        # → WeatherData
news_list = fetch_news(["科技", "综合"])    # → list[NewsItem]
```

---

### 4.3 AI 大模型调用模块 (`ai/`) — 刘志杰

#### 功能需求

- 接入三家大模型 SDK（DeepSeek / 智谱AI / 通义千问）
- 所有模型通过统一基类 `AIModel` 暴露 `generate_brief()` 方法
- 输入标准化天气 + 新闻数据 → 输出标准化 `BriefReport`
- 支持提示词配置化（可调整语气、长度、格式）
- 处理 API 超时、Token 溢出、返回格式异常等边界情况

#### 架构设计

```
                    ┌───────────┐
                    │  AIModel  │ ← 基类 (开发者实现)
                    │ .generate_brief() │
                    └──────┬──────┘
                           │ 继承
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
   ┌─────────────┐  ┌──────────┐  ┌──────────┐
   │ DeepSeekBot │  │ ZhipuBot │  │ QwenBot  │
   │ (deepseek_) │  │(zhipu-)  │  │(qwen-)   │
   └─────────────┘  └──────────┘  └──────────┘
```

#### 技术实现

```python
# ai/base.py — AIModel 抽象基类 (已完成)
from abc import ABC, abstractmethod
from models.weather import WeatherData
from models.news import NewsItem
from models.brief import BriefReport

class AIModel(ABC):
    """AI模型基类，所有模型适配器必须继承并实现 generate_brief"""

    model_name: str = ""
    model_display: str = ""

    @abstractmethod
    def generate_brief(self,
                       weather: WeatherData,
                       news: list[NewsItem]) -> BriefReport:
        """输入天气+新闻素材，输出标准化BriefReport"""
        raise NotImplementedError

    def _build_prompt(self, weather: WeatherData, news: list[NewsItem]) -> str:
        """组装发送给AI的提示词（已实现）

        提示词结构：
        1. 角色设定（你是一个专业晨间简报助手）
        2. 天气数据段落（调用 weather.summary_text()）
        3. 新闻数据段落（编号标题+摘要）
        4. 未来天气预报
        5. 输出格式要求（天气一段话、综合简报 200-400 字）
        6. 语气约束（温暖友好、简体中文、纯文本不用 Markdown）
        """
        # 已实现，各适配器无需重写

    def _parse_response(self, raw_response: str,
                        weather: WeatherData,
                        news: list[NewsItem]) -> BriefReport:
        """解析 AI 响应为 BriefReport（已实现默认版本）
        各适配器可按需覆盖此方法。"""
        # 已实现：将响应填入 weather_summary + digest
```

```python
# ai/deepseek.py — DeepSeek 适配器 (骨架已就绪，待填充)
from ai.base import AIModel, AModelError
class DeepSeekBot(AIModel):
    model_name = "deepseek"
    model_display = "DeepSeek"

    def _get_client(self):
        # TODO: 刘志杰 — 初始化 OpenAI 兼容客户端
        # 参考: https://api-docs.deepseek.com/
        pass

    def generate_brief(self, weather, news):
        prompt = self._build_prompt(weather, news)
        # TODO: 刘志杰 — 调用 DeepSeek API 并返回 BriefReport
        raise AModelError("DeepSeek 模型接入待实现")
```

```python
# ai/zhipu.py — 智谱AI 适配器 (骨架已就绪，待填充)
# TODO: 刘志杰 — 参考 https://open.bigmodel.cn/dev/api
# 使用 zhipuai SDK

# ai/qwen.py — 通义千问 适配器 (骨架已就绪，待填充)
# TODO: 刘志杰 — 参考 https://help.aliyun.com/zh/dashscope/
# 使用 dashscope SDK
```

#### 提示词工程要点

```
提示词输入内容：
├── 天气数据（城市、温度、状况、风力、湿度、未来3日预报）
├── 新闻素材（标题+摘要列表，3-5条）
└── 用户偏好（可选的语气/格式要求）

提示词输出要求：
├── weather_summary: 一段话（100字以内）→ 口语化天气摘要
├── digest: 一段话（200-400字）→ 综合简报
│           包含：天气感受 + 今日重点新闻 + 一句话总结
└── model_used: 标识使用的模型
```

#### 对接接口

```python
# 调用方：brief_service
from ai.deepseek import DeepSeekBot
from ai.zhipu import ZhipuBot
from ai.qwen import QwenBot

# 根据用户选择创建对应模型实例
models = {
    "deepseek": DeepSeekBot,
    "zhipu": ZhipuBot,
    "qwen": QwenBot,
}
bot = models["deepseek"]()
brief = bot.generate_brief(weather, news_list)  # → BriefReport
```

---

### 4.4 数据持久化模块 (`storage/`) — 崔锦崧

#### 功能需求

- 保存/加载用户偏好配置（城市、新闻类别、首选模型）
- 保存/查询/列表历史简报
- 同时支持 JSON 文件和 SQLite 两种存储后端
- 通过 `STORAGE_BACKEND` 环境变量切换
- 文件不阻塞启动，存储不可用时返回默认值

#### 架构设计

```
              ┌───────────┐
              │ Storage   │ ← 基类 (开发者实现)
              │ .save_brief() │
              │ .get_brief()  │
              │ .list_briefs()│
              │ .save_prefs() │
              │ .load_prefs() │
              └──────┬──────┘
                     │ 继承
          ┌──────────┴──────────┐
          ▼                    ▼
  ┌──────────────┐    ┌──────────────┐
  │JsonStore     │    │SqliteStore   │
  │(data/        │    │(data/        │
│ store.json)    │    │ store.db)     │
  └──────────────┘    └──────────────┘
```

#### 技术实现

```python
# storage/base.py — Storage 抽象基类 (已完成)
from abc import ABC, abstractmethod
from models.brief import BriefReport
from models.prefs import UserPrefs

class Storage(ABC):
    """存储基类，所有后端必须实现以下方法"""

    @abstractmethod
    def save_brief(self, brief: BriefReport) -> None: ...

    @abstractmethod
    def get_brief(self, date: str) -> Optional[BriefReport]: ...

    @abstractmethod
    def list_briefs(self, limit: int = 10) -> list: ...

    @abstractmethod
    def save_prefs(self, prefs: UserPrefs) -> None: ...

    @abstractmethod
    def load_prefs(self) -> UserPrefs: ...
```

### 已实现后端

**JsonStore** (`storage/json_store.py`) — ✅ 已实现
- 数据存储于 `data/store.json`
- 写入前自动备份为 `.json.bak`，写入失败自动恢复
- 自动创建 `data/` 目录
- 同日期 `save_brief()` 覆盖更新

**SqliteStore** (`storage/sqlite_store.py`) — ✅ 已实现
- 数据存储于 `data/store.db`
- 初始化时自动建表 `briefs` (含 PK date) + `prefs` (key-value)
- 新闻列表存为 JSON 字符串
- `load_prefs()` 空库时返回 `UserPrefs.default()`

### 工厂函数

```python
# storage/__init__.py
from storage import create_storage

storage = create_storage()  # 根据 STORAGE_BACKEND 环境变量自动选择后端
# json (默认) → JsonStore
# sqlite → SqliteStore
```

#### 数据流

```
前端修改设置 → save_prefs(UserPrefs)
              │
              ├──→ STORAGE_BACKEND=json  → 写入 data/store.json
              └──→ STORAGE_BACKEND=sqlite → 写入 data/store.db

简报生成完成 → save_brief(BriefReport)
              │
              ├──→ 同上逻辑
              └──→ 关联 date 字段索引

前端请求历史 → list_briefs(limit=10)
              │
              ├──→ 按 created_at 倒序返回
              └──→ 返回 BriefReport 对象列表
```

#### 对接接口

```python
# 调用方：前端、brief_service
from storage import create_storage

storage = create_storage()  # 根据环境变量自动选择后端

# 偏好
prefs = storage.load_prefs()
storage.save_prefs(prefs)

# 简报
storage.save_brief(brief)
briefs = storage.list_briefs(limit=10)
```

---

### 4.5 核心编排模块 (`services/brief_service.py`) — 刘奕铮

#### 功能定位

这是整个项目的**中枢模块**。所有其他模块只暴露原子能力，本模块负责串联完整流程。

#### 技术实现

```python
# services/brief_service.py — 简报生成中枢
from models.prefs import UserPrefs
from models.brief import BriefReport
from api.weather_api import fetch_weather
from api.news_api import fetch_news
from ai.deepseek import DeepSeekBot
from ai.zhipu import ZhipuBot
from ai.qwen import QwenBot
from storage import create_storage

def generate_morning_brief(prefs: UserPrefs = None, city: str = None, model: str = None, categories: list = None, news_limit: int = 5) -> BriefReport:
    """按用户偏好执行完整简报流程

    流程:
    1. 获取天气数据
    2. 获取新闻数据
    3. 调用 AI 模型生成简报
    4. 保存到存储
    5. 返回 BriefReport
    """
    # 1. 天气
    weather = fetch_weather(prefs.city)

    # 2. 新闻
    news_list = fetch_news(prefs.news_categories, limit=5)

    # 3. AI 生成简报
    models = {
        "deepseek": DeepSeekBot,
        "zhipu": ZhipuBot,
        "qwen": QwenBot,
    }
    bot = models[prefs.ai_model]()
    brief = bot.generate_brief(weather, news_list)

    # 4. 保存
    storage = create_storage()
    storage.save_brief(brief)

    # 5. 返回
    return brief
```

---

### 4.6 配置模块 (`config/`) — 刘奕铮

```python
# config/settings.py
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env
load_dotenv(Path(__file__).parent.parent / ".env")

_settings = {}

def get(key: str, default=None):
    """获取配置项"""
    import os
    return _settings.get(key) or os.environ.get(key, default)
```

```python
# config/constants.py
CITIES = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "南京"]
NEWS_CATEGORIES = ["科技", "财经", "体育", "综合"]
AI_MODELS = {
    "deepseek": "DeepSeek",
    "zhipu": "智谱AI",
    "qwen": "通义千问",
}
```

---

### 4.7 工具函数模块 (`utils/`)

```
utils/date_utils.py    → 日期格式化 (YYYY-MM-DD / 中文星期 / 友好时间)
utils/format_utils.py  → 文本截断 / 空值处理 / Markdown 转 Streamlit
utils/validators.py    → 城市名验证 / 参数范围检查
```

---

## 5. 核心业务流程

### 5.1 用户生成简报流程（完整数据流）

```
用户操作: 设置好城市/类别/模型 → 点击"生成今日简报"
                        │
                        ▼
            ┌───────────────────────────────┐
            │   Streamlit 前端 (app.py)      │
            │   读取 UserPrefs              │
            │   触发 generate_morning_brief()│
            └─────────────┬─────────────────┘
                          │
                          ▼
            ┌───────────────────────────────┐
            │   brief_service.py            │
            │   (核心编排)                   │
            └─────────────┬─────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
  ┌───────────────┐ ┌──────────┐  ┌──────────┐
  │ fetch_weather │ │ fetch_   │  │ AIModel  │
  │ ("北京")      │ │ news()   │  │.generate_ │
  └───────┬───────┘ └────┬─────┘  │ brief()   │
          │               │        └──────────┘
          ▼               ▼
  {"城市ID" ──→ "和风JSON" │  {"标题","摘要"...}
   "实时"   ──→ "现在JSON" │
   "7天"    ──→ "预报JSON" │ WeatherData     NewsItem[]
          │               │
          └───────┬───────┘
                  ▼
        ┌───────────────────────┐
        │   AI 提示词:          │
        │   "天气:{...}+新闻:{...│
        │   → 生成简报"         │
        └─────────┬─────────────┘
                  ▼
         BriefReport 对象
                  │
                  ▼
        ┌───────────────────────┐
        │ save_brief()          │
        │ (写入存储)            │
        └─────────┬─────────────┘
                  ▼
        Streamlit 前端渲染展示
        (天气摘要 + 简报正文 + 新闻卡片)
```

### 5.2 流程时序图

```
用户           前端             brief_service        天气API         新闻API         AI模型          存储
 │               │                    │                 │              │              │              │
 │ 点击生成简报   │                    │                 │              │              │              │
 │──────────────>│                    │                 │              │              │              │
 │               │ generate_brief()   │                 │              │              │              │
 │               │───────────────────>│                 │              │              │              │
 │               │                    │ fetch_weather() │              │              │              │
 │               │                    │────────────────>│              │              │              │
 │               │                    │WeatherData      │              │              │              │
 │               │                    │<────────────────│              │              │              │
 │               │                    │                 │  fetch_news() │              │              │
 │               │                    │                 │──────────────>│              │              │
 │               │                    │                 │   NewsItem[]  │              │              │
 │               │                    │                 │<──────────────│              │              │
 │               │                    │generate_brief() │              │              │              │
 │               │                    │────────────────────────────────────────────────>│              │
 │               │                    │ BriefReport     │              │              │              │
 │               │                    │<────────────────────────────────────────────────│              │
 │               │                    │ save_brief()    │              │              │              │
 │               │                    │────────────────────────────────────────────────────────────>│
 │               │ BriefReport        │                 │              │              │              │
 │               │<───────────────────│                 │              │              │              │
 │ 渲染简报页面   │                    │                 │              │              │              │
 │<──────────────│                    │                 │              │              │              │
```

### 5.3 关键处理说明

**异常处理**：
- 天气/新闻 API 请求失败 → 返回错误消息给用户，流程中止
- AI 请求超时 → 捕获异常，提示用户稍后重试
- 存储不可用 → 提示"暂无法保存历史"，不影响当前简报展示

**加载状态**：
- 整个流程预计 3-10 秒，前端展示统一 Loading 动画
- 分步反馈：正在获取天气 → 正在获取新闻 → AI 正在生成 → 完成

---

## 6. 数据存储约定

### 6.1 JSON 存储格式 (`data/store.json`)

```json
{
  "prefs": {
    "city": "北京",
    "news_categories": ["科技", "综合"],
    "ai_model": "deepseek",
    "briefing_time": "08:00"
  },
  "briefs": [
    {
      "date": "2026-07-08",
      "city": "北京",
      "weather_summary": "今天北京晴，气温22-28度...",
      "news_items": [
        {
          "title": "...",
          "summary": "...",
          "source": "...",
          "category": "科技",
          "url": "https://...",
          "publish_time": "2026-07-08 06:30"
        }
      ],
      "digest": "今天是7月8日...",
      "model_used": "deepseek",
      "created_at": "2026-07-08T08:15:00"
    }
  ]
}
```

### 6.2 SQLite 表结构 (`data/store.db`)

```sql
CREATE TABLE IF NOT EXISTS briefs (
    date          TEXT    NOT NULL,
    city          TEXT    NOT NULL,
    weather_summary TEXT,
    news_items    TEXT,       -- JSON 字符串
    digest        TEXT,
    model_used    TEXT,
    created_at    TEXT    NOT NULL,
    PRIMARY KEY (date)
);

CREATE TABLE IF NOT EXISTS prefs (
    key   TEXT PRIMARY KEY,
    value TEXT    NOT NULL
);
```

---

## 7. API Key 管理

### 7.1 环境变量清单

| 变量名 | 用途 | 提供方 |
|--------|------|--------|
| `QWEATHER_KEY` | 和风天气 API | https://console.qweather.com/ |
| `NEWS_KEY` | 新闻 API | 待定 |
| `DEEPSEEK_KEY` | DeepSeek API | https://platform.deepseek.com/ |
| `ZHIPU_KEY` | 智谱AI API | https://open.bigmodel.cn/ |
| `QWEN_KEY` | 通义千问 API | https://dashscope.console.aliyun.com/ |

### 7.2 使用方式

```bash
# 复制模板
cp .env.example .env

# 编辑 .env 填入真实 Key
```

**安全注意**：`.env` 文件在 `.gitignore` 中，绝不提交到版本库。

---

## 8. 依赖清单

```txt
# requirements.txt
streamlit>=1.30.0
requests>=2.31.0
python-dotenv>=1.0.0
pydantic>=2.5.0
# 以下为可选，由各模块按需添加
zhipuai>=2.0.0            # 智谱AI SDK
dashscope>=1.14.0         # 通义千问 SDK
openai>=1.0.0             # DeepSeek (兼容 OpenAI 接口协议)
```

---

## 9. 运行方式

### 9.1 本地开发

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Key

# 3. 启动
streamlit run run.py
```

启动后默认访问 `http://localhost:8501`

---

## 10. 项目路线图

### Phase 1: 框架搭建 ✅ 已完成
- [x] AGENTS.md — 协作规范与技术标准
- [x] SPEC.md — 本文档
- [x] 目录结构 + 35 个文件
- [x] 4 个数据模型（WeatherData / NewsItem / BriefReport / UserPrefs）含双向序列化
- [x] 配置模块（Settings 单例 + 17 项常量）
- [x] API 调用钩子（weather_api.py + news_api.py，含 TODO 和参考文档）
- [x] AI 模型骨架（AIModel ABC 基类 + _build_prompt + _parse_response + 3 个 Bot）
- [x] 存储双后端（JsonStore + SqliteStore，均已完整实现）
- [x] 核心编排（brief_service.py 5 步流水线）
- [x] 定时调度器（SimpleScheduler + 全局 start/stop）
- [x] 公共工具函数（15 个：日期/格式化/验证）
- [x] Streamlit 前端主页面 + 设置页 + 10 个 UI 组件
- [x] 项目入口 run.py
- [x] 测试骨架（16 个测试用例）
- [x] 文档（README / CONTRIBUTING / LICENSE / AGENTS / SPEC）
- [x] 框架全面审查（语法/导入/接口/功能 全通过）

### Phase 2: 并行开发
- [ ] 前端界面完善 (芦泓天)
- [ ] 天气 API 实现 (芦泓天) — 参考和风天气文档
- [ ] 新闻 API 实现 (芦泓天) — 确定新闻源
- [ ] AI 模型接入 (刘志杰) — 填充 3 个 Bot 的 generate_brief
- [x] 存储模块完善 (崔锦崧) — 2026-07-09 补全 13 个专项测试 + 模块 README

### Phase 3: 集成测试
- [ ] 功能联调（API + AI 全部接入后）
- [ ] Bug 修复
- [ ] 文档完善

### Phase 4: 发布
- [ ] 创建 Release + Tag
- [ ] 编写 Release Notes
- [ ] 部署上线

---

## 附录 A: 术语表

| 术语 | 说明 |
|------|------|
| **MornDigest** | 项目名，即晨间简报 |
| **简报** | 包含天气摘要 + 新闻摘要 + AI综合评述的完整报告 |
| **BriefReport** | 简报的标准数据结构对象 |
| **UserPrefs** | 用户偏好的标准数据结构对象 |
| **API** | 外部数据接口（和风天气、新闻API、AI大模型） |
| **Streamlit** | Python 交互式 Web 框架 |
| **Branch** | Git 分支，各模块在独立分支开发 |
| **PR (Pull Request)** | 合并请求，功能完成后提交PR合并到主分支 |

## 附录 B: 模块快速导航

拿到这个文档后，根据你的分工快速定位：

| 你是 | 重点看 |
|------|-------|
| 前端开发 (芦泓天) | 章节 4.1, 4.2, 5 |
| AI模型接入 (刘志杰) | 章节 4.3, 5 |
| 数据存储 (崔锦崧) | 章节 4.4, 6 |
| 框架基建 (刘奕铮) | 章节 3, 4.5, 4.6 |
| 拓展功能 (刘诗钰) | 章节 5, 8 |

## 附录 C: 工具函数详情

### 日期工具 (`utils/date_utils.py`)

| 函数 | 签名 | 返回值 | 示例 |
|------|------|--------|------|
| `today()` | `() -> str` | `YYYY-MM-DD` | `"2026-07-08"` |
| `today_with_weekday()` | `() -> str` | `YYYY-MM-DD 星期` | `"2026-07-08 星期三"` |
| `friendly_time()` | `(dt: datetime) -> str` | 友好格式 | `"2026-07-08 14:30"` |
| `add_days()` | `(d: str, days: int) -> str` | 计算后日期 | `"2026-07-11"` |
| `format_timestamp()` | `(ts: float) -> str` | 时间戳转字符串 | `"2026-07-08 10:30:00"` |

### 格式化工具 (`utils/format_utils.py`)

| 函数 | 签名 | 说明 |
|------|------|------|
| `truncate(text, max_length, suffix)` | 超出长度截断并加后缀 | `"Hello World" → "Hello…"` |
| `empty_to_default(value, default)` | 空值返回默认串 | `None → "未知"` |
| `clean_empty_lines(text, max_empty)` | 清理多余空行 | 连续空行合并 |
| `markdown_to_plain(md_text)` | Markdown 转纯文本 | `**粗体** → 粗体` |
| `wrap_text(text, line_length)` | 按字数换行 | 长文本自动换行 |

### 数据验证 (`utils/validators.py`)

| 函数 | 签名 | 说明 | 异常 |
|------|------|------|------|
| `validate_city(city)` | `(str) -> str` | 自动去空格，空值报错 | `ValueError` |
| `validate_model(model_name)` | `(str) -> str` | 转小写，不在候选列表报错 | `ValueError` |
| `validate_categories(categories)` | `(list) -> list` | 非空检查，过滤非法值 | `ValueError` |
| `validate_positive_int(value, max_value, field_name)` | `(int, int, str) -> int` | 正整数且不超过最大值 | `ValueError` |
| `validate_time_range(time_str)` | `(str) -> str` | 验证 HH:MM 格式 | `ValueError` |

## 附录 D: 测试指南

### 运行测试

```bash
pytest tests/          # 运行全部测试
pytest tests/ -v       # 详细输出
pytest tests/test_brief_flow.py -v  # 指定文件
pytest tests/test_storage.py -v     # 只跑 storage 专项
```

### 当前测试覆盖（29 个用例 = 16 流程 + 13 storage 专项）

| 类别 | 测试函数 | 覆盖内容 |
|------|----------|----------|
| **数据模型** | `test_weather_data_to_dict` | WeatherData 序列化 |
| | `test_weather_data_from_dict` | WeatherData 反序列化 |
| | `test_news_item_serialization` | NewsItem 双向序列化 |
| | `test_brief_report_with_news` | BriefReport 嵌套 NewsItem 序列化/反序列化 |
| | `test_user_prefs_default` | UserPrefs 默认值 |
| **配置** | `test_settings_get` | Settings.get() 基本读取 |
| | `test_constants_exist` | 常量模块导入 + 值验证 |
| **工具函数** | `test_validate_city` | 城市验证（正常+异常） |
| | `test_validate_model` | 模型验证（正常+异常） |
| | `test_validate_categories` | 分类验证（正常+异常） |
| | `test_truncate` | 文本截断（正常/超限） |
| | `test_date_utils` | 日期工具函数 |
| **AI 骨架** | `test_ai_model_raises` | 基类正确抛出异常 |
| | `test_deepseek_bot_instantiable` | DeepSeekBot 可实例化 |
| | `test_zhipu_bot_instantiable` | ZhipuBot 可实例化 |
| | `test_qwen_bot_instantiable` | QwenBot 可实例化 |
| **Storage 专项** | `test_sqlite_init_creates_db_file` 等 8 例 | SqliteStore 初始化 / 父目录 / CRUD / 覆盖 / 默认回退 |
| | `test_json_save_then_get_brief` 等 3 例 | JsonStore CRUD / 覆盖 / 偏好 |
| | `test_create_storage_defaults_to_json` 等 2 例 | 工厂默认 + env 切换 |

### 添加新测试

遵循以下规范：
- 测试函数命名为 `test_功能名`
- 每个测试只验证一个逻辑点
- 异常行为使用 `pytest.raises()` 捕获
- 测试独立运行，不依赖文件系统
