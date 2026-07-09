## 任务：生成 AGENTS.md 项目协作与技术规范文件

在 `E:\MornDigest\AGENTS.md` 创建一个完整的项目规范文档，包含以下内容：

1. **技术栈总览** — Python 3.10+, Streamlit, 三家AI大模型, 和风天气, SQLite/JSON双存储, GitHub/Vercel
2. **项目目录结构** — 完整树形结构，标注每个目录归属和负责人，以及模块边界规则
3. **数据模型标准** (章节 3) — WeatherData / NewsItem / BriefReport / UserPrefs 四个类的字段定义表格 + snake_case 命名规则
4. **模块接口规范** (章节 4) — 5 组调用钩子的函数签名 + 调用方/实现方标注：
   - `api/weather_api.py` → `fetch_weather(city) -> WeatherData`
   - `api/news_api.py` → `fetch_news(categories, limit) -> list[NewsItem]`
   - `ai/base.py` → `AIModel.generate_brief()` 基类
   - `storage/base.py` → `Storage` 基类 CRUD
   - `services/brief_service.py` → 核心编排入口
5. **配置与环境变量** (章节 5) — .env 模板 + settings 访问方式
6. **Git 协作规范** (章节 6) — 分支策略 + Commit 格式 + PR 流程
7. **编码规范** (章节 7) — 缩进/注释/导入顺序/错误处理/适用代码风格
8. **团队分工表** (章节 8) — 姓名 ↔ 模块 ↔ 目录
9. **数据存储约定** (章节 9) — data/ 目录 + Git 排除
10. **开发工具须知** (章节 10) — AI 工具规范

**操作**：在 `E:\MornDigest` 目录下用 `Write` 工具创建 `AGENTS.md` 文件（纯文本操作，无其他文件改动）。