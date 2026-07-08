# Contributing to MornDigest

感谢你参与 MornDigest 项目的开发！以下指南帮助你快速上手协作。

---

## 1. 开发流程

### 1.1 标准工作流

```
查看/创建 Issue → 认领任务 → 创建功能分支 → 开发 → 本地自测 → 提交 PR → 他人 Review → 合并到 main
```

### 1.2 分支策略

```
main                     ← 稳定线，直接可运行
├── feature/frontend     ← 前端界面开发（芦泓天）
├── feature/weather-news ← 天气&新闻数据源（芦泓天）
├── feature/ai-models    ← AI模型接入（刘志杰）
├── feature/storage      ← 存储模块（崔锦崧）
└── feature/extensions   ← 拓展功能（刘诗钰）
```

**规则：**
- 所有新功能从 `main` 分支拉取
- 开发完成后通过 Pull Request 合并回 `main`
- 合并后删除功能分支

### 1.3 创建分支

```bash
# 拉取最新 main
git fetch origin main
git switch main
git pull

# 创建功能分支
git switch -c feature/your-feature-name
```

---

## 2. Commit 规范

### 2.1 格式

```
[type] 简短描述

可选详细说明...
```

### 2.2 Type 类型

| Type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `[feat] 实现天气数据获取` |
| `fix` | Bug 修复 | `[fix] 修复新闻分页偏移错误` |
| `docs` | 文档变更 | `[docs] 更新README项目说明` |
| `refactor` | 代码重构（不改变功能） | `[refactor] 简化brief_service逻辑` |
| `test` | 测试相关 | `[test] 添加简报生成流程测试` |
| `chore` | 其他杂项（依赖、配置等） | `[chore] 更新依赖版本` |

### 2.3 提交代码

```bash
git add .
git commit -m "[feat] 你的描述"
git push -u origin feature/your-feature-name
```

---

## 3. Pull Request 流程

### 3.1 提交 PR

1. 确保你的功能分支已推送到远程（`git push`）
2. 在 GitHub 仓库页面点击 **"Compare & pull request"**
3. 填写 PR 标题和描述

### 3.2 PR 描述模板

```markdown
## 改动摘要
（简要说明本次 PR 做了什么）

## 相关 Issue
Closes #issue-number

## 测试
- [ ] 本地自测通过
- [ ] 项目可正常启动运行

## 备注
（可选：需要 Reviewer 特别关注的点）
```

### 3.3 Review 规则

- **至少 1 人** Review 通过后方可合并
- Reviewer 关注：功能是否正确、代码规范性、是否影响其他模块

---

## 4. 本地开发

### 4.1 环境搭建

```bash
# 1. 克隆仓库
git clone https://github.com/Bistu-OSSDT-2026/MornDigest.git
cd MornDigest

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或: venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Key

# 5. 启动
streamlit run run.py
```

### 4.2 运行测试

```bash
pytest tests/             # 运行全部测试
pytest tests/ -v          # 详细输出
pytest tests/test_brief_flow.py -v  # 运行指定文件
```

### 4.3 常用命令

```bash
# 查看状态
git status

# 拉取最新代码
git pull

# 查看提交历史
git log --oneline -10

# 查看分支
git branch -a
```

---

## 5. 编码规范

详见 [AGENTS.md](AGENTS.md) 第 7 节 编码规范。要点：

- **缩进**：4 空格，不用 Tab
- **注释**：每个公共函数写中文 docstring（说明功能、入参、出参）
- **导入顺序**：标准库 → 第三方库 → 项目内部
- **错误处理**：不吞异常（不写空 `except: pass`）
- **模块隔离**：不修改其他模块目录的文件

---

## 6. 模块职责

| 人员 | 负责模块 | 目录 | 当前状态 |
|------|----------|------|----------|
| 刘奕铮 | 框架基建 + 核心编排 | `config/` `models/` `services/` `utils/` | ✅ 已完成 |
| 芦泓天 | 前端界面 | `frontend/` | ✅ 骨架完成 |
| 芦泓天 | 天气&新闻数据源 | `api/` | ⬜ 待填充 TODO |
| 刘志杰 | AI 模型接入 | `ai/` | ⬜ 待填充 TODO |
| 崔锦崧 | 数据持久化 | `storage/` | ✅ 双后端已完成 |
| 刘诗钰 | 拓展功能 + 自测 + 文档 | `tests/` 文档 | ✅ 骨架完成 |

**如何开始**：
- 找到你的 TODO 文件（列表见 [AGENTS.md 附录 A](AGENTS.md#-附录-a-待实现-todo-清单)）
- 从 `main` 拉取功能分支
- 只修改 `# TODO: 你的名字` 标记处及内部逻辑
- 修改完成后本地运行 `pytest tests/` 确认无回归

---

## 7. 项目文档

| 文档 | 内容 |
|------|------|
| [README.md](README.md) | 项目说明、快速开始 |
| [AGENTS.md](AGENTS.md) | 协作规范、技术栈、接口定义 |
| [SPEC.md](SPEC.md) | 产品规格、系统设计、数据流 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 本文档 |
| [requirements.txt](requirements.txt) | Python 依赖清单 |

如有疑问，请及时在小组群内沟通，或向对应模块负责人提问。
