# storage — 数据持久化模块

> **负责人**：崔锦崧
> **接口稳定性**：✅ 已被 `services/` 与 `frontend/` 锁定，禁止随意改名 / 改签名

本模块为 MornDigest 提供**统一的数据访问层**。所有模块通过 `from storage import create_storage` 拿到一个 `Storage` 子类实例，再调用其方法操作数据。**严禁**业务代码直接 import `sqlite3` / `json` / 文件路径。

---

## 1. 文件清单

| 文件 | 作用 |
|------|------|
| `__init__.py` | 重新导出 `Storage` / `StorageError` / `JsonStore` / `SqliteStore` / `create_storage` 工厂 |
| `base.py` | `Storage` 抽象基类（5 个抽象方法）+ `StorageError` 异常 |
| `sqlite_store.py` | SQLite 后端实现，数据存于 `data/store.db` |
| `json_store.py` | JSON 后端实现，数据存于 `data/store.json`（带 `.bak` 自动备份） |

---

## 2. 统一接口（`Storage` 基类）

所有后端**必须**实现以下 5 个方法，签名与返回类型**已锁定**：

| 方法 | 签名 | 返回 | 说明 |
|------|------|------|------|
| `save_brief` | `(brief: BriefReport) -> None` | — | 保存简报（同日期覆盖更新） |
| `get_brief` | `(date: str) -> Optional[BriefReport]` | 简报对象或 `None` | 按日期查询 |
| `list_briefs` | `(limit: int = 10) -> list[BriefReport]` | 简报列表 | 按 `created_at` 倒序 |
| `save_prefs` | `(prefs: UserPrefs) -> None` | — | 保存用户偏好 |
| `load_prefs` | `() -> UserPrefs` | 偏好对象 | 不存在时返回 `UserPrefs.default()` |

> 接口源：`storage/base.py`。README 仅做导航，**修改签名前必须更新基类与所有调用方**。

---

## 3. 工厂函数 `create_storage()`

```python
from storage import create_storage

storage = create_storage()  # 自动根据 STORAGE_BACKEND 环境变量选择后端
```

| `STORAGE_BACKEND` 值 | 返回的后端类 | 数据文件 |
|---------------------|-------------|---------|
| `json`（**默认**） | `JsonStore` | `data/store.json` |
| `sqlite` | `SqliteStore` | `data/store.db` |
| 未设置 / 其他值 | `JsonStore` | `data/store.json` |

> 环境变量读取忽略大小写，详见 `config/constants.py::DEFAULT_STORAGE_BACKEND`。

---

## 4. 快速上手

### 4.1 保存 & 查询简报

```python
from datetime import datetime
from storage import create_storage
from models.brief import BriefReport

storage = create_storage()

# 保存
brief = BriefReport(
    date="2026-07-09",
    city="北京",
    weather_summary="今天北京晴",
    news_items=[],
    digest="完整简报正文",
    model_used="deepseek",
    created_at=datetime.now(),
)
storage.save_brief(brief)

# 按日期查
loaded = storage.get_brief("2026-07-09")
print(loaded.digest if loaded else "未找到")

# 查最近 10 条
history = storage.list_briefs(limit=10)
for b in history:
    print(b.date, b.city)
```

### 4.2 保存 & 读取用户偏好

```python
from storage import create_storage
from models.prefs import UserPrefs

storage = create_storage()

# 加载（空库时自动返回 UserPrefs.default()）
prefs = storage.load_prefs()
print(prefs.city, prefs.ai_model, prefs.news_categories)

# 修改后保存
prefs.city = "上海"
prefs.ai_model = "zhipu"
storage.save_prefs(prefs)
```

---

## 5. 数据契约与限制

### 5.1 同日期简报

`save_brief()` **按日期去重**：同一 `date` 第二次保存会**覆盖**前一次，不会新增条目。
两个后端均通过 PK 约束 / 列表内查找实现此行为。

### 5.2 失败行为

- **SqliteStore**：建表 / 写入抛 `sqlite3.Error` 时，**异常向上传播**。调用方需自行捕获。
- **JsonStore**：写入失败时尝试从 `.json.bak` 恢复，恢复成功记录 `ERROR` 日志、否则抛 `StorageError`。

### 5.3 时间格式

`BriefReport.created_at` 以 `"%Y-%m-%dT%H:%M:%S"`（ISO 8601 无时区）形式序列化，对应 `config.constants.TIMESTAMP_FORMAT`。

---

## 6. 为什么没有 `save_report` / `get_reports` 等别名？

任务描述中的函数命名：

| 任务描述中的命名 | 实际等价方法 |
|-----------------|-------------|
| `save_report(city, content, model, create_time)` | `save_brief(BriefReport(...))` |
| `get_reports()` | `list_briefs(limit=10)` |
| `save_user_config(...)` | `save_prefs(UserPrefs(...))` |
| `get_user_config()` | `load_prefs()` |

设计选择：

1. **保持 dataclass 边界**：`BriefReport` / `UserPrefs` 是项目统一的数据契约（见 `models/`），所有跨模块传参都走 dataclass。如果新增 `save_report(city, content, model, create_time)` 这样的"裸字段"接口，要么把其他字段（`weather_summary` / `news_items`）丢掉，要么再加更多参数——都会让 API 变得不一致。
2. **接口已锁定**：`services/brief_service.py` 和 `frontend/pages/settings.py` 已经在使用 `save_brief` / `list_briefs` / `load_prefs` / `save_prefs`。新增别名只会让团队困惑哪个是"正典"。
3. **遵循单一数据契约**：所有持久化操作围绕 `BriefReport` / `UserPrefs` 两个 dataclass 进行，避免散落的字段式 API。

如果你希望调用方**只传几个字段**，请先构造 dataclass 再传入：

```python
from models.brief import BriefReport
storage.save_brief(BriefReport(
    date="2026-07-09", city=city, weather_summary="",
    digest=content, model_used=model, created_at=create_time,
))
```

---

## 7. 扩展指引：增加新后端

如果未来要支持 MySQL / PostgreSQL / Redis 等：

1. 新建文件 `storage/<name>_store.py`，定义 `class <Name>Store(Storage)`，实现 5 个抽象方法。
2. 在 `storage/__init__.py` 的 `create_storage()` 中追加分支并加入 `__all__`。
3. **不要**修改 `base.py` 的抽象方法签名——任何签名变更都意味着所有调用方要同步改。

---

## 8. 测试

`tests/test_storage.py` 提供 13 个核心用例，覆盖：

- SqliteStore 8 个：初始化、CRUD、覆盖、默认回退
- JsonStore 3 个：CRUD、覆盖
- Factory 2 个：env 切换

运行：

```bash
pytest tests/test_storage.py -v
```

所有测试使用 pytest `tmp_path` 隔离，**不会**污染项目根目录的 `data/`。
