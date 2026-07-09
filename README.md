# MornDigest

> AI晨间智能简报工具 — 自动化信息聚合，个性化晨间简报

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.1.0-green.svg)](https://github.com/Bistu-OSSDT-2026/MornDigest/releases)

## 项目简介

MornDigest 是一款轻量化个人信息聚合网页程序，如同你专属的私人助理，每日自动汇总天气、新闻等多类信息，经由 AI 大模型智能处理，生成结构清晰的晨间简报。

## ✨ 核心功能

- **🌤 天气聚合**：和风天气实时数据 + 预报信息
- **📰 新闻聚合**：多分类资讯自动收集
- **🤖 AI 简报**：支持 DeepSeek / 智谱AI / 通义千问 三选一生成智能简报
- **⚙️ 个性化偏好**：自定义城市、新闻类型、AI 模型
- **💾 历史存储**：自动生成并保存历史简报记录（JSON / SQLite 双后端）
- **📱 轻量 Web**：纯浏览器访问，无需安装

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

需要以下 API Key：

| Key | 用途 | 获取地址 |
|-----|------|---------|
| `QWEATHER_KEY` | 和风天气 | https://console.qweather.com/ |
| `NEWS_KEY` | 新闻接口 | 待定 |
| `DEEPSEEK_KEY` | DeepSeek | https://platform.deepseek.com/ |
| `ZHIPU_KEY` | 智谱AI | https://open.bigmodel.cn/ |
| `QWEN_KEY` | 通义千问 / 阿里云百炼 | https://dashscope.console.aliyun.com/ 或 https://bailian.console.aliyun.com/ |

> **百炼平台说明**：`QWEN_KEY` 同时支持阿里云 DashScope 和百炼（Bailian）平台。百炼平台上还可调用第三方模型（如 `glm-5.1`），具体可用模型见 `ai/qwen.py` 中的 `_QWEN_MODEL` 注释。

### 3. 启动应用

```bash
streamlit run run.py
```

打开浏览器访问 `http://localhost:8501` 即可使用。

### 4. 运行测试

```bash
pytest tests/            # 运行全部 47 个测试用例
pytest tests/ -v         # 详细输出
```

### 5. 真机测试 AI 模型（快速验证 key 可用）

```bash
# Windows PowerShell
$env:QWEN_KEY = "sk-your-bailian-key"
$env:PYTHONIOENCODING = "utf-8"
python scripts\test_qwen_bailian.py
```

详见 `scripts/test_qwen_bailian.py`。

## 📁 项目结构

```
MornDigest/
├── config/       # 配置管理 (Settings单例 + 常量)
├── models/       # 全局数据模型 (WeatherData / NewsItem / BriefReport / UserPrefs)
├── api/          # 外部 API 接口（天气、新闻）→ 芦泓天
├── ai/           # AI 大模型调用 (AIModel基类 + 3适配器，已完成) → 刘志杰
├── storage/      # 数据持久化（JSON / SQLite 双后端）→ 崔锦崧
├── frontend/     # Streamlit 前端（主页面 + 设置页 + UI组件）→ 芦泓天
├── services/     # 业务逻辑编排（简报生成 + 定时调度）
├── utils/        # 公共工具函数（日期/格式化/验证）
├── tests/        # 测试（47 个用例）→ 刘诗钰
├── scripts/      # 辅助脚本（如百炼真机测试）
├── run.py        # 项目入口
├── AGENTS.md     # 协作规范与技术标准
├── SPEC.md       # 产品规格与技术设计文档
└── data/         # 运行时数据（不提交 Git）
```

> 完整目录结构（含每个文件）见 [AGENTS.md](AGENTS.md) 第 2 节。

## 📄 文档

| 文档 | 内容 |
|------|------|
| [AGENTS.md](AGENTS.md) | 协作规范、技术栈、目录结构、数据模型、**完整接口签名**、配置、Git 规范、编码规范、运行与测试、TODO 清单 |
| [SPEC.md](SPEC.md) | 产品规格、功能清单、系统架构、模块详细设计、核心业务流程、数据流图、存储格式、路线图、测试指南 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Git 协作指南、分支策略、Commit 规范、PR 流程、本地开发环境搭建 |

## 👥 团队

| 人员 | 职责 | 负责模块 | 当前状态 |
|------|------|----------|----------|
| 刘奕铮 | 框架基建 + 核心编排 | `config/` `models/` `services/` `utils/` | ✅ 框架搭建完毕 |
| 芦泓天 | 前端 & 数据源 | `frontend/` `api/` | 进行中 |
| **刘志杰** | **AI 模型接入** | **`ai/`** | **✅ 已完成** |
| 崔锦崧 | 数据持久化 | `storage/` | ✅ 双后端均实现 |
| 刘诗钰 | 拓展功能 & 自测 & 文档 | `tests/` `scripts/` 文档 | 进行中 |

## 🏗 项目进度

| 模块 | 状态 | 说明 |
|------|------|------|
| 配置管理 (`config/`) | ✅ 完成 | Settings 单例 + 17 项常量 |
| 数据模型 (`models/`) | ✅ 完成 | 4 个 dataclass + 双向序列化 |
| 数据持久化 (`storage/`) | ✅ 完成 | JSON + SQLite 双后端 |
| 核心编排 (`services/brief_service.py`) | ✅ 完成 | 5 步流水线 + 模型工厂 |
| **AI 大模型 (`ai/`)** | **✅ 完成** | **DeepSeek / 智谱GLM / 通义Qwen 三家适配** |
| 前端界面 (`frontend/`) | 🚧 进行中 | Streamlit 主页面 + 设置页 |
| 天气 & 新闻 API (`api/`) | 🚧 进行中 | 待填充 SDK 调用 |
| 单元测试 (`tests/`) | ✅ 47 个用例 | 数据模型/配置/工具/AI 全部覆盖 |
| 定时调度 (`services/scheduler.py`) | ⏳ 待开发 | 拓展功能 |

## 📜 开源协议

MIT License — 详见 [LICENSE](LICENSE)