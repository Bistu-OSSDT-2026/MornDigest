# MornDigest — 项目协作与技术规范

> AI晨间智能简报工具 — 轻量化个人信息聚合网页，如私人助理般每日自动汇总多类信息生成晨间简报。
>
> **最后更新**: 2026-07-09 16:10:00
> **更新者**: 刘奕铮（框架搭建与审查完毕）; 崔锦崧（storage 模块补全 + 文档同步）

---

## 📌 本版本变更日志 (2026-07-09 崔锦崧)

本人在本分支对项目做以下改动（不影响现有任何代码接口）：

| 类别 | 文件 | 改动 |
|------|------|------|
| 新增 | `tests/test_storage.py` | 13 个 storage 专项测试（SqliteStore 8 + JsonStore 3 + 工厂 2） |
| 新增 | `storage/README.md` | storage 模块使用文档（接口 / 调用示例 / 后端切换 / 扩展指引） |
| 修改 | `AGENTS.md` | §8 崔锦崧状态补全；§11.2 测试数 16→29；§11.3 加 storage 测试条目 |
| 修改 | `SPEC.md` | §10 路线图 Phase 2 存储模块勾选完成；附录 D 测试数 16→29 并加 storage 类别 |
| 修改 | `README.md` | 修复合并冲突标记（`<=======>` 残留）；功能/结构/状态中同步 storage 测试覆盖 |

**接口影响**：**零**。`storage/` 下的 `__init__.py` / `base.py` / `sqlite_store.py` / `json_store.py` 四个文件**完全未动**，`save_brief` / `list_briefs` / `save_prefs` / `load_prefs` 五个公开方法签名不变。

**测试结果**：`pytest tests/ -v` → 29 passed。

---

## 1. 技术栈

| 层面 | 技术 | 说明 |
|------|------|------|
| **语言** | Python 3.10+ | 全栈统一 Python，不混用多语言 |
| **前端** | Streamlit | 轻量级 Python Web 框架，无需 HTML/JS |
| **AI 大模型** | DeepSeek / 智谱AI / 通义千问 | 三家全接入，支持前端切换 |
| **天气 API** | 和风天气 (QWeather) | 实时天气 + 预报 |
| **新闻 API** | News 新闻接口 | 多类别资讯聚合 |
| **数据存储** | SQLite + JSON 文件双方案 | 存储模块已实现，由环境变量切换 |
| **配置管理** | python-dotenv + Settings 单例 | 读取 .env 文件，全局 `settings.get()` 访问 |
| **数据模型** | dataclass + to_dict/from_dict 双向序列化 | 模块间通过标准数据类传递 |
| **代码管理** | GitHub | 仓库: `Bistu-OSSDT-2026/MornDigest` |
| **部署** | Vercel / 本地演示 | 皆可 |
| **测试** | pytest | 运行 `pytest tests/` |
| **AI 编程工具** | Claude Code / Codex / Cursor / ZCode | 允许辅助编码，但必须吃透自身模块逻辑 |

---

## 2. 项目目录结构

```
MornDigest/
├── README.md                    # 项目说明、快速开始
├── AGENTS.md                    # 本文档 — 协作规范与技术标准
├── SPEC.md                      # 产品规格与技术设计文档
├── LICENSE                      # MIT 开源协议
├── CONTRIBUTING.md              # Git 协作指南
├── .gitignore                   # Git 忽略规则
├── requirements.txt             # Python 依赖清单
├── .env.example                 # 环境变量模板（不含密钥）
├── run.py                       # 项目入口，启动 Streamlit
│
├── config/                      # 配置管理 (负责人: 刘奕铮)
│   ├── __init__.py              # 重新导出 settings + constants
│   ├── settings.py              # Settings 单例，读取 .env
│   └── constants.py             # 常量：城市/新闻/模型/超时等
│
├── models/                      # 全局数据模型 (负责人: 刘奕铮)
│   ├── __init__.py              # 重新导出 4 个数据类
│   ├── weather.py               # WeatherData dataclass
│   ├── news.py                  # NewsItem dataclass
│   ├── brief.py                 # BriefReport dataclass (含嵌套序列化)
│   └── prefs.py                 # UserPrefs dataclass (含 __post_init__ + default())
│
├── api/                         # 外部 API 接口 (负责人: 芦泓天)
│   ├── __init__.py              # 重新导出 fetch_weather, fetch_news, Error
│   ├── weather_api.py           # 天气模块 (TODO: 填充和风天气调用逻辑)
│   └── news_api.py              # 新闻模块 (TODO: 填充新闻 API 调用逻辑)
│
├── ai/                          # AI 模型调用 (负责人: 刘志杰)
│   ├── __init__.py              # 重新导出 AIModel, AModelError, 3个Bot
│   ├── base.py                  # AIModel ABC基类 + _build_prompt + _parse_response
│   ├── deepseek.py              # DeepSeekBot (兼容 OpenAI 协议)
│   ├── zhipu.py                 # ZhipuBot (zhipuai SDK)
│   └── qwen.py                  # QwenBot (dashscope SDK)
│
├── storage/                     # 数据持久化 (负责人: 崔锦崧)
│   ├── __init__.py              # 重新导出 + create_storage() 工厂函数
│   ├── base.py                  # Storage ABC基类 (定义 5 个抽象方法)
│   ├── sqlite_store.py          # SqliteStore (已实现，自动建表)
│   └── json_store.py            # JsonStore (已实现，含写入前备份)
│
├── frontend/                    # Streamlit 前端 (负责人: 芦泓天)
│   ├── __init__.py              # 模块说明
│   ├── app.py                   # 主页面：标题/侧边栏/生成按钮/简报展示/错误提示
│   ├── pages/
│   │   ├── __init__.py          # Streamlit 多页面支持
│   │   └── settings.py          # 设置页：城市/分类/模型/时间 + 保存/预览
│   └── components.py            # 10 个可复用 UI 组件函数
│
├── services/                    # 业务逻辑编排 (负责人: 刘奕铮)
│   ├── __init__.py              # 重新导出 7 个公共服务函数
│   ├── brief_service.py         # 简报生成中枢 + get_ai_bot() 工厂 + get_recent_briefs()
│   └── scheduler.py             # 定时调度器 (负责人: 刘诗钰)
│
├── utils/                       # 公共工具函数 (负责人: 刘奕铮)
│   ├── __init__.py              # 重新导出 15 个工具函数
│   ├── date_utils.py            # today / today_with_weekday / friendly_time / add_days / format_timestamp
│   ├── format_utils.py          # truncate / empty_to_default / clean_empty_lines / markdown_to_plain / wrap_text
│   └── validators.py            # validate_city / validate_model / validate_categories / validate_positive_int / validate_time_range
│
├── tests/                       # 测试 (负责人: 刘诗钰)
│   ├── __init__.py              # 模块说明
│   └── test_brief_flow.py       # 16 个测试用例 (模型/配置/工具/AI骨架)
│
└── data/                        # 运行时数据 (在 .gitignore 中)
    ├── store.json               # JSON 存储后端文件 (自动创建)
    └── store.db                 # SQLite 存储后端文件 (自动创建)
```

**目录规则**：每个模块只在自己负责的目录内编写代码，不主动修改其他模块目录的文件。跨模块协调通过 `models/` 定义的数据结构和框架预留的调用接口完成。

---

## 3. 数据模型标准

所有模块间数据交互通过 `models/` 中定义的标准类传递。每个数据类均实现了 `to_dict()` / `from_dict()` 双向序列化。

### 3.1 WeatherData — 天气数据

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `city` | `str` | `""` | 城市名 |
| `date` | `str` | `""` | 日期，格式 `YYYY-MM-DD` |
| `temp_now` | `float` | `0.0` | 当前温度 (°C) |
| `temp_min` | `float` | `0.0` | 当日最低温度 |
| `temp_max` | `float` | `0.0` | 当日最高温度 |
| `condition` | `str` | `""` | 天气状况（晴/多云/阴/雨/雪等） |
| `humidity` | `int` | `0` | 相对湿度 (%) |
| `wind_level` | `str` | `""` | 风力等级 |
| `forecast` | `list` | `[]` | 未来 3 日简况列表 |
| `source` | `str` | `"qweather"` | 来源标识 |
| `timestamp` | `datetime` | `datetime.now()` | 数据获取时间 |

**方法**：`to_dict()`, `from_dict(d)`, `summary_text()`, `is_valid()`

### 3.2 NewsItem — 新闻条目

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `title` | `str` | `""` | 标题 |
| `summary` | `str` | `""` | 摘要/导语 |
| `source` | `str` | `""` | 来源媒体名称 |
| `category` | `str` | `""` | 分类 |
| `url` | `str` | `""` | 原文链接 |
| `publish_time` | `str` | `""` | 发布时间 |

**方法**：`to_dict()`, `from_dict(d)`, `is_valid()`

### 3.3 BriefReport — 简报输出

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `date` | `str` | `""` | 简报日期 `YYYY-MM-DD` |
| `city` | `str` | `""` | 目标城市 |
| `weather_summary` | `str` | `""` | AI 生成的天气摘要 |
| `news_items` | `list[NewsItem]` | `[]` | 关联新闻列表 |
| `digest` | `str` | `""` | AI 生成的简报正文 |
| `model_used` | `str` | `""` | 使用的模型 |
| `created_at` | `datetime` | `datetime.now()` | 创建时间 |

**方法**：`to_dict()` (自动嵌套序列化 NewsItem), `from_dict(d)` (自动反序列化), `is_valid()`, `word_count()`

> **注意**：BriefReport 的 `news_items` 字段包含嵌套对象，`to_dict()` / `from_dict()` 会自动处理嵌套序列化/反序列化。

### 3.4 UserPrefs — 用户偏好

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `city` | `str` | `None → "北京"` | 默认城市 |
| `news_categories` | `list[str]` | `None → ["科技", "综合"]` | 感兴趣的新闻分类 |
| `ai_model` | `str` | `None → "deepseek"` | 首选 AI 模型 |
| `briefing_time` | `str` | `None → "08:00"` | 简报推送时间 `HH:MM` |

**`__post_init__`**：会自动将 None 字段填充为默认值。

**方法**：`to_dict()`, `from_dict(d)`, `default()` (工厂函数，返回默认配置)

### 3.5 命名规则

- **JSON 字段**统一使用 **snake_case**（如 `temp_now`），不使用 camelCase
- 模块间传递数据对象**引用**，不在返回结构里嵌错误码
- 异常情况通过 **抛出异常**（带明确 `message`）处理
- 所有序列化字段名与 Python 属性名保持一致

---

## 4. 模块接口规范

> 以下接口签名已被系统验证，跨模块调用均已通过。请勿修改函数签名，仅可在函数体内填充实现逻辑。

### 4.1 配置模块 (`config/`)

**公共接口**：

```python
# 方式一：从 config 包直接导入
from config import settings, CITIES, NEWS_CATEGORIES, AI_MODELS, DEFAULT_CITY, DEFAULT_MODEL

# 方式二：从子模块导入
from config.settings import settings
from config.constants import CITIES, API_TIMEOUT, AI_MODELS
```

**Settings 单例方法**：

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `settings.get(key, default)` | `str, str` | `str` | 获取字符串配置 |
| `settings.get_list(key, sep=',', default)` | `str, str, str` | `list[str]` | 获取逗号分隔列表 |
| `settings.get_int(key, default)` | `str, int` | `int` | 获取整数配置 |
| `settings.get_bool(key, default)` | `str, bool` | `bool` | 获取布尔配置 |
| `settings.all()` | — | `dict` | 获取所有环境变量 |

**常量清单**：

```python
CITIES                  # list[str], 30 个中国主要城市
NEWS_CATEGORIES         # list[str], ["科技", "财经", "体育", "综合"]
AI_MODELS               # dict, {"deepseek": "DeepSeek", "zhipu": "智谱AI", "qwen": "通义千问"}
DEFAULT_CITY            # str, "北京"
DEFAULT_MODEL           # str, "deepseek"
DEFAULT_CATEGORIES      # list[str], ["科技", "综合"]
DEFAULT_NEWS_LIMIT      # int, 5
DEFAULT_FORECAST_DAYS   # int, 3
DEFAULT_STORAGE_BACKEND # str, "json"
DATE_FORMAT             # str, "%Y-%m-%d"
DATETIME_FORMAT         # str, "%Y-%m-%d %H:%M:%S"
TIMESTAMP_FORMAT        # str, "%Y-%m-%dT%H:%M:%S"
API_TIMEOUT             # int, 15
APP_NAME                # str, "MornDigest"
APP_VERSION             # str, "0.1.0"
APP_DESCRIPTION         # str
```

### 4.2 天气模块 (`api/weather_api.py`)

```python
from api.weather_api import fetch_weather, WeatherAPIError

def fetch_weather(city: str) -> WeatherData:
    """从和风天气API获取指定城市天气数据
    内部子函数: _get_location_id, _get_realtime_weather, _get_forecast, _build_weather_data
    """
    # TODO: 芦泓天 — 实现和风天气 API 调用
    # 参考文档: https://dev.qweather.com/docs/api/
```

**调用方**：`services/brief_service.py`
**实现方**：芦泓天

### 4.3 新闻模块 (`api/news_api.py`)

```python
from api.news_api import fetch_news, NewsAPIError

def fetch_news(categories: list = None, limit: int = 5) -> list[NewsItem]:
    """按类别获取新闻列表
    内部子函数: _fetch_category_news, _map_category
    实现逻辑: 遍历分类 → 请求API → 去重 → 截断 → 返回
    """
    # TODO: 芦泓天 — 实现新闻 API 调用
```

**调用方**：`services/brief_service.py`
**实现方**：芦泓天

### 4.4 AI 模型模块 (`ai/`)

```python
# 基类
from ai.base import AIModel, AModelError

# 适配器
from ai.deepseek import DeepSeekBot
from ai.zhipu import ZhipuBot
from ai.qwen import QwenBot
```

**AIModel 基类接口**：

| 属性 | 类型 | 说明 |
|------|------|------|
| `model_name` | `str` | 模型标识 (deepseek / zhipu / qwen) |
| `model_display` | `str` | 模型显示名 |

| 方法 | 签名 | 类型 | 说明 |
|------|------|------|------|
| `generate_brief` | `(weather: WeatherData, news: list) -> BriefReport` | **abstract** | 已由三家 Bot 实现 |
| `_build_prompt` | `(weather: WeatherData, news: list) -> str` | default | 基类已实现完整提示词模板 |
| `_parse_response` | `(raw_response: str, weather: WeatherData, news: list) -> BriefReport` | default | **三家 Bot 各自覆盖**，按"1.天气摘要 / 2.简报正文"切两段 |

**基类内置 `_build_prompt()` 提示词结构**：
1. 角色设定（专业晨间简报助手）
2. 天气数据段落
3. 新闻数据段落
4. 输出格式要求（天气100字以内 + 简报200-400字）
5. 语气约束（温暖友好、纯文本、不用Markdown）

**三家 Bot 实现要点**（已完成）：

| 适配器 | 模型名 | SDK | Base URL / 配置 | 异常处理 |
|--------|--------|-----|------------------|----------|
| `DeepSeekBot` | `deepseek-chat` | `openai>=1.0.0` | `https://api.deepseek.com/v1` | `AuthenticationError` / `APITimeoutError` / `APIConnectionError` / `APIError` 分别捕获 |
| `ZhipuBot` | `glm-4-flash` | `zhipuai>=2.0.0` | 默认 | `APIAuthenticationError` / `APITimeoutError` / `APIConnectionError` / `APIStatusError` / `ZhipuAIError` 分别捕获 |
| `QwenBot` | `qwen-plus`（可改） | `dashscope>=1.14.0` | 默认 | 手动检查 `status_code == 200`，捕获网络/SDK 异常 |

**懒加载**：`_get_client()` / `_get_api_key()` 只在首次调用时读取 key，未配置时抛 `AModelError` 并附带明确的 key 名称提示。

**备选模型**（修改 `ai/qwen.py` 的 `_QWEN_MODEL` 一行即可切换）：
- `qwen-turbo`：更快，便宜
- `qwen-plus`：默认，综合强
- `qwen-max`：最强
- `qwen-long`：超长上下文（适合大量新闻）
- `glm-5.1`：智谱 GLM 系列（百炼平台提供）

**真机测试脚本**：`scripts/test_qwen_bailian.py` — 填入 key 后一键验证 Qwen 调用效果。

**SDK 参考**：
- DeepSeek: [api-docs.deepseek.com](https://api-docs.deepseek.com/) — 兼容 OpenAI 协议，使用 `openai` SDK
- 智谱AI: [open.bigmodel.cn/dev/api](https://open.bigmodel.cn/dev/api) — 使用 `zhipuai` SDK
- 通义千问: [help.aliyun.com/zh/dashscope](https://help.aliyun.com/zh/dashscope/) — 使用 `dashscope` SDK
- 阿里云百炼: [bailian.console.aliyun.com](https://bailian.console.aliyun.com/) — 与 DashScope 同 API

**调用方**：`services/brief_service.py`
**实现方**：刘志杰（**✅ 已完成**）

### 4.5 存储模块 (`storage/`)

```python
# 工厂函数（推荐方式）
from storage import create_storage

# 也可直接导入具体实现
from storage.base import Storage, StorageError
from storage.json_store import JsonStore
from storage.sqlite_store import SqliteStore
```

**Storage 基类抽象方法**（所有实现必须提供）：

| 方法 | 签名 | 返回 | 说明 |
|------|------|------|------|
| `save_brief` | `(brief: BriefReport) -> None` | — | 保存简报（同日期覆盖更新） |
| `get_brief` | `(date: str) -> BriefReport` | `BriefReport \| None` | 按日期查询 |
| `list_briefs` | `(limit: int = 10) -> list` | list[BriefReport] | 按时间倒序列表（仅 limit 参数） |
| `save_prefs` | `(prefs: UserPrefs) -> None` | — | 保存偏好 |
| `load_prefs` | `() -> UserPrefs` | `UserPrefs` | 读取偏好（空时返回默认值） |

**工厂函数**：

```python
storage = create_storage()  # 读取 STORAGE_BACKEND 环境变量
# json (默认) → JsonStore(data/store.json)
# sqlite → SqliteStore(data/store.db)
```

**已实现特性**：
- **JsonStore**：自动创建 data/ 目录、写入前备份 `.json.bak`、写入失败自动恢复
- **SqliteStore**：自动建表（`CREATE TABLE IF NOT EXISTS`）、新闻列表存 JSON 字符串

**调用方**：`services/brief_service.py`, `frontend/app.py`, `frontend/pages/settings.py`
**实现方**：崔锦崧

### 4.6 简报服务 (`services/brief_service.py`)

```python
from services.brief_service import generate_morning_brief, get_ai_bot, get_recent_briefs
```

| 函数 | 签名 | 返回 | 说明 |
|------|------|------|------|
| `generate_morning_brief` | `(prefs=None, city=None, model=None, categories=None, news_limit=5) -> BriefReport` | BriefReport | **核心编排入口** |
| `get_ai_bot` | `(model_name: str) -> AIModel` | AIModel实例 | 模型工厂，无效名时抛出 AModelError |
| `get_recent_briefs` | `(limit: int = 10) -> list` | list[BriefReport] | 获取历史简报 |

**`generate_morning_brief` 完整流程**：
```
步骤 1: fetch_weather(city)         → WeatherData
步骤 2: fetch_news(categories, limit) → list[NewsItem]
步骤 3: get_ai_bot(model).generate_brief(weather, news) → BriefReport
步骤 4: create_storage().save_brief(brief)
步骤 5: return brief
```

**参数优先级**：显式参数 > prefs 对象 > 默认值

**错误处理策略**：
- 天气/新闻 API 失败 → 异常向上传播，前端捕获并展示
- AI 模型失败 → 异常向上传播
- 存储保存失败 → **记录警告日志，不影响当前简报展示**（降级处理）

**实现方**：刘奕铮

### 4.7 定时调度器 (`services/scheduler.py`)

```python
from services.scheduler import start_scheduler, stop_scheduler, is_scheduler_running
```

| 函数 | 说明 |
|------|------|
| `start_scheduler(callback, interval_seconds)` | 启动全局定时任务（默认每小时执行一次） |
| `stop_scheduler()` | 停止定时任务 |
| `is_scheduler_running() -> bool` | 检查调度器是否在运行 |

底层基于 `threading.Timer` 实现，生产环境可替换为 APScheduler。

**实现方**：刘诗钰

### 4.8 工具函数 (`utils/`)

```python
from utils.date_utils import today, today_with_weekday, friendly_time, add_days, format_timestamp
from utils.format_utils import truncate, empty_to_default, clean_empty_lines, markdown_to_plain, wrap_text
from utils.validators import validate_city, validate_model, validate_categories, validate_positive_int, validate_time_range
```

| 文件 | 函数 | 说明 |
|------|------|------|
| `date_utils.py` | `today()` | 返回 `YYYY-MM-DD` |
| | `today_with_weekday()` | 返回 `YYYY-MM-DD 星期X` |
| | `friendly_time(dt)` | 友好时间格式 |
| | `add_days(d, days)` | 日期加减天数 |
| | `format_timestamp(ts)` | 时间戳转字符串 |
| `format_utils.py` | `truncate(text, max_length)` | 超出长度截断并加 `…` |
| | `empty_to_default(value, default)` | 空值返回默认串 |
| | `clean_empty_lines(text, max_empty)` | 清理多余空行 |
| | `markdown_to_plain(md_text)` | Markdown 转纯文本 |
| | `wrap_text(text, line_length)` | 按字数换行 |
| `validators.py` | `validate_city(city)` | 验证城市名（自动去空格） |
| | `validate_model(model_name)` | 验证模型名（自动转小写） |
| | `validate_categories(categories)` | 验证分类列表（非空） |
| | `validate_positive_int(value, max_value, field_name)` | 正整数范围检查 |
| | `validate_time_range(time_str)` | 验证 `HH:MM` 格式时间 |

**实现方**：刘奕铮

### 4.9 前端组件 (`frontend/components.py`)

```python
from frontend.components import (
    render_weather_card,   # 天气卡片
    render_news_card,      # 新闻卡片
    render_news_list,      # 新闻列表
    render_digest,         # 简报正文
    render_loading,        # 加载动画
    render_error,          # 错误提示
    render_info,           # 信息提示
    render_success,        # 成功提示
    render_header,         # 页面标题栏
    render_sidebar,        # 侧边栏快捷设置 → 返回 dict {city, model, categories}
)
```

**实现方**：芦泓天

---

## 5. 配置与环境变量

### 5.1 环境变量文件 (`.env`)

复制 `.env.example` 为 `.env` 并填入真实 Key：

```env
# 外部 API Key
QWEATHER_KEY=...
NEWS_KEY=...

# AI 模型 API Key
DEEPSEEK_KEY=...
ZHIPU_KEY=...
QWEN_KEY=...

# 应用配置
DEFAULT_CITY=北京
DEFAULT_MODEL=deepseek
DEFAULT_CATEGORIES=科技,综合
STORAGE_BACKEND=json    # json 或 sqlite
APP_LANG=zh-CN
```

**.env 不提交到版本库**，提交前请确认 `.env` 在 `.gitignore` 中。

### 5.2 配置访问

```python
from config import settings

api_key = settings.get("QWEATHER_KEY")
city = settings.get("DEFAULT_CITY", "北京")
cats = settings.get_list("DEFAULT_CATEGORIES")       # → ["科技", "综合"]
timeout = settings.get_int("API_TIMEOUT", 15)         # → 15
debug = settings.get_bool("DEBUG_MODE", False)        # → False
all_env = settings.all()                              # → dict[str, str]
```

---

## 6. Git 协作规范

### 6.1 分支策略

```
main                     ← 稳定线，直接可运行
├── feature/frontend     ← 前端界面开发（芦泓天）
├── feature/weather-news ← 天气&新闻数据源（芦泓天）
├── feature/ai-models    ← AI模型接入（刘志杰）
├── feature/storage      ← 存储模块完善（崔锦崧）
└── feature/extensions   ← 拓展功能（刘诗钰）
```

- 从 `main` 拉取新分支开发
- 开发完成后通过 **Pull Request** 合并回 `main`
- 合并后删除功能分支
- **不要直接在 main 上 commit**

### 6.2 Commit 规范

```
[type] 简短中文描述

type:  feat | fix | docs | refactor | test | chore

示例：
[feat] 实现天气数据获取钩子
[fix] 修复新闻分页偏移错误
[docs] 更新 README 项目说明
[refactor] 简化 brief_service 逻辑
[test] 添加简报生成流程测试
[chore] 更新依赖版本
```

### 6.3 PR 流程

1. 确认 Issue 或群内已描述要做什么
2. 从 `main` 拉最新代码后新建功能分支
3. 开发完成后本地自测（`pytest tests/` + 能启动）
4. 提交 PR，描述改动摘要
5. **至少 1 人 Review** 通过后合并

---

## 7. 编码规范

### 7.1 通用

- 代码语言：**Python**
- 缩进：**4 空格**（不用 Tab）
- 编码：UTF-8
- 单文件不超过 300 行

### 7.2 注释

- 每个公共函数写中文 docstring，说明功能、入参、出参
- 复杂逻辑用行内注释解释 *为什么*，不是 *做了什么*
- 示例：
```python
def fetch_weather(city: str) -> WeatherData:
    """从和风天气API获取指定城市天气数据

    Args:
        city: 城市名，如 "北京"

    Returns:
        WeatherData: 标准化天气数据对象

    Raises:
        WeatherAPIError: 当 API 请求失败时抛出
    """
```

### 7.3 导入顺序

```python
# 1. 标准库
import os
from datetime import datetime

# 2. 第三方库
import requests
from pydantic import BaseModel

# 3. 项目内部
from config.settings import settings
from models.weather import WeatherData
```

### 7.4 错误处理

- **不吞异常**：不写空的 `except: pass`
- 外部 API 请求失败抛明确异常，含原始错误信息
- 日志用 `logging` 模块，不低于 `INFO` 级别
- 各模块自定义异常：`WeatherAPIError`, `NewsAPIError`, `AModelError`, `StorageError`

### 7.5 命名规范

- 函数/变量/模块：**snake_case**
- 类名：**PascalCase**
- 常量：**UPPER_SNAKE_CASE**
- 私有方法/属性：前缀 `_`

---

## 8. 团队分工

| 人员 | 负责模块 | 目录 | 当前状态 |
|------|----------|------|----------|
| 刘奕铮 | 框架基建 + 核心编排 | `config/` `models/` `services/` `utils/` | **已完成** 框架搭建 |
| 芦泓天 | 前端界面 + 数据源 | `frontend/` `api/` | 待填充 TODO |
| 刘志杰 | AI 模型接入 | `ai/` | 待填充 TODO |
| 崔锦崧 | 数据持久化 | `storage/` | **已完成**（双后端 + 13 个专项测试 + README） |
| 刘诗钰 | 拓展功能 + 自测 + 文档 | `tests/` 文档 | 骨架已完成 |
| 刘奕铮 | 框架基建 + 核心编排 | `config/` `models/` `services/` `utils/` | ✅ 框架搭建完毕 |
| 芦泓天 | 前端界面 + 数据源 | `frontend/` `api/` | 🚧 进行中 |
| **刘志杰** | **AI 模型接入** | **`ai/`** | **✅ 已完成**（三家模型 + 31 个单测 + 真机验证脚本） |
| 崔锦崧 | 数据持久化 | `storage/` | ✅ 双后端均实现 |
| 刘诗钰 | 拓展功能 + 自测 + 文档 | `tests/` `scripts/` 文档 | 🚧 进行中 |

---

## 9. 数据存储约定

- `data/` 目录存放运行时数据，已在 `.gitignore` 中排除
- JSON 存储：`data/store.json`（含自动备份 `.json.bak`）
- SQLite 存储：`data/store.db`（自动建表 `briefs` + `prefs`）
- 由 `STORAGE_BACKEND` 环境变量切换（`json` / `sqlite`）
- **同日期更新**：`save_brief()` 若同日期已存在，则覆盖更新而非新增

---

## 10. 开发工具须知

- 允许使用 AI 编程工具辅助编码（Claude Code / Codex / Cursor / ZCode 等）
- **必须吃透自身负责模块的逻辑**，能独立解释和调试自己的代码
- 提交的代码需本地验证可运行，不提交含 placeholder 的半成品
- 使用 AI 工具生成的代码需自行审核后再提交

---

## 11. 运行与测试

### 11.1 快速启动

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env  # 编辑 .env 填入 API Key

# 启动应用
streamlit run run.py   # 访问 http://localhost:8501
```

### 11.2 运行测试

```bash
# 运行全部测试
pytest tests/

# 详细输出
pytest tests/ -v

# 运行单个测试文件
pytest tests/test_brief_flow.py -v
```

当前测试覆盖 **29 个用例**（16 个流程 + 13 个 storage 专项）：
- 6 个数据模型测试（序列化/反序列化/嵌套/默认值）
- 2 个配置测试（settings + constants）
- 5 个工具函数测试（验证器 + 格式化工具 + 日期工具）
- 3 个 AI 骨架测试（3 个 Bot 可实例化 + 基类异常）
- 13 个 storage 专项测试（SqliteStore 8 + JsonStore 3 + Factory 2，详见 `storage/README.md` §8）
当前测试覆盖 **47 个用例**（31 新增 + 16 原有）：
- 6 个数据模型测试（序列化/反序列化/嵌套/默认值）
- 2 个配置测试（settings + constants）
- 5 个工具函数测试（验证器 + 格式化工具 + 日期工具）
- **31 个 AI 模块测试**（`tests/test_ai_bots.py`）：
  - 3 个 Bot 类签名（model_name/model_display/inheritance）
  - 2 个 services.get_ai_bot 工厂
  - 4 个缺失 API Key 行为
  - 4 个 _build_prompt 渲染（含空新闻兜底）
  - 8 个 _parse_response 解析（标准格式/纯段落/单段/空响应/news_items/created_at/date兜底）
  - 4 个三家 Provider 端到端 mock（deepseek/zhipu/qwen + settings key 来源）
  - 6 个异常分类（鉴权/超时/连接/接口/空内容）

### 11.3 框架审查记录

| 检查项 | 结果 |
|--------|------|
| 35 个 .py 文件语法检查 | ✅ 全部通过 |
| 模块导入检查 | ✅ 全部通过 |
| 继承关系验证（3 Bot → AIModel, 2 Store → Storage） | ✅ 全部通过 |
| 函数签名检查（10 个跨模块接口） | ✅ 一致 |
| 数据模型双向序列化 | ✅ 通过 |
| 嵌套序列化（BriefReport → NewsItem） | ✅ 通过 |
| 验证函数（5 个） | ✅ 通过 |
| 工具函数（10 个） | ✅ 通过 |
| JsonStore CRUD + 更新覆盖 | ✅ 通过 |
| SqliteStore CRUD + 默认回退 | ✅ 通过 |
| **storage 专项测试 13 例 + 模块 README**（崔锦崧 2026-07-09 补全） | ✅ 通过 |
| AI 模块骨架（实例化 + 异常 + 提示词） | ✅ 通过 |

---

## 附录 A: 待实现 TODO 清单

| 文件 | 负责人 | 内容 | 状态 |
|------|--------|------|------|
| `api/weather_api.py` | 芦泓天 | 实现和风天气 3 步调用（地理编码 → 实时天气 → 预报） | ⏳ |
| `api/news_api.py` | 芦泓天 | 实现新闻 API 请求 + 分类映射 | ⏳ |
| ~~`ai/deepseek.py`~~ | ~~刘志杰~~ | ~~初始化 OpenAI 兼容客户端 + 调用 DeepSeek API~~ | **✅ 已完成** |
| ~~`ai/zhipu.py`~~ | ~~刘志杰~~ | ~~初始化 zhipuai 客户端 + 调用智谱 API~~ | **✅ 已完成** |
| ~~`ai/qwen.py`~~ | ~~刘志杰~~ | ~~初始化 dashscope + 调用通义千问 API~~ | **✅ 已完成** |

---

## 附录 B: 框架搭建过程中修复的 Bug

| # | 问题 | 文件 | 修复内容 |
|---|------|------|----------|
| 1 | `storage/__init__.py` 中多余的 `logger_created = SqliteStore()` 赋值 | `storage/__init__.py` | 删除冗余行，保留 `return SqliteStore()` |
| 2 | `frontend/components.py` render_sidebar 含破坏性代码 `tag = "{}"` 和 `list({}.format(...))` | `frontend/components.py` | 重写 render_sidebar 函数，使用固定模型列表 |
| 3 | `ai/__init__.py` 中 `__all__` 拼写错误（与 base.py 不一致） | `ai/__init__.py` | 统一为 `AModelError`，与 base.py 保持一致 |
| 4 | `config/__init__.py` 未导出 constants 模块 | `config/__init__.py` | 补充 re-export 所有常量 |
| 5 | `SPEC.md` 中 `storage.factory` 路径错误 | `SPEC.md` | 修正为 `from storage import create_storage` |