# 🎭 dprofile

[![PyPI version](https://img.shields.io/pypi/v/dprofile.svg)](https://pypi.org/project/dprofile/)
[![Python versions](https://img.shields.io/pypi/pyversions/dprofile.svg)](https://pypi.org/project/dprofile/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/pythias/dprofile/actions/workflows/ci.yml/badge.svg)](https://github.com/pythias/dprofile/actions/workflows/ci.yml)

**为 AI Agent 量身定制的人格套装切换工具。**

`dprofile` 是一个安全、确定性的人格切换工具，专为现代 Agent 时代设计。它将 `USER.md`、`SOUL.md` 和 `AGENTS.md` 视为一个原子化的“人格套装”，让开发者和 Agent 都能在毫秒间完成身份切换。

本项目以 `SKILL.md` 作为 Agent 的主入口，负责定义工作流和安全规则。CLI 是次级的确定性执行器，也提供无 skill 场景下的 fallback 指南。

[English Version](README.md)

---

## ✨ 核心特性

- **🤖 Agent 原生设计**：支持 Agent 自主调用以进化自身身份或配置子 Agent 任务。
- **🛡️ 安全第一**：自动备份、状态追踪，并对目标目录进行严格的安全性验证。
- **🏗️ 三层人格模型**：
    - `USER.md`：你正在帮助谁（用户背景与偏好）。
    - `SOUL.md`：你是谁（身份认同与价值观）。
    - `AGENTS.md`：你如何工作（工具协议与工作流）。
- **🔗 混合写入模式**：支持 **符号链接**（实时同步更新）或 **物理复制**（便于移植导出）。

## 🚀 快速开始

先安装 Agent skill。在你的 Agent 里直接说：

```text
从 github.com/pythias/dprofile 安装 dprofile skill。
```

安装 skill 后，让 Agent 使用某个 profile：

```text
在这个项目里用 Codex 使用 coding profile。
```

Agent 应该读取 `SKILL.md`，判断目标类型，然后选择正确操作。对代码项目来说，通常会通过 `dprofile init` 生成 adapter 文件。

CLI 是可选项，但建议安装，方便确定性执行：

```bash
pip install dprofile
```

---

## 📖 使用模式

### 1. Agent 配置目录
Agent 利用 `dprofile` 在 Agent 自己拥有的配置目录中切换身份，或配置专门的协作节点。

```bash
# Agent 操作指令示例：“将我的 Codex 人格切换为 'architect'（架构师）。”
dprofile switch architect --target-dir ~/.codex
```

### 2. 代码项目
代码项目可能同时被多种 Agent 和 IDE 打开，因此 `dprofile` 将 `USER.md`、`SOUL.md`、`AGENTS.md` 视为 profile 源文件，而不是默认丢进仓库根目录的最终文件。

对于项目目录，请遵循 `SKILL.md` 中的 adapter 工作流：先生成到 `.dprofile/generated/<adapter>/`，再按需激活具体 Agent 文件，例如 `CLAUDE.md`、`.cursor/rules/dprofile.mdc`、`.github/copilot-instructions.md`、`GEMINI.md` 或 `AGENTS.md`。

不同 adapter 不会拿到完全相同的源层。Claude 和 Gemini 使用完整 profile 上下文；Cursor、Copilot、Codex、OpenCode 默认只使用操作协议层，避免把完整用户/人格上下文写进项目级规则。

```bash
# 为单个 AI 助手安装项目指令
dprofile init coding --target-dir . --ai codex

# 同时为多个助手安装
dprofile init coding --target-dir . --ai claude,cursor,copilot

# 只生成，不激活原生文件
dprofile apply coding --target-dir . --agents all
```

### 3. 可选 CLI（人工或自动化）
开发者可以直接管理 Agent 自己拥有的配置目录。

```bash
# 列出所有可用人格
dprofile list

# 将专用 Agent 配置目录切换为 'coding'（编码）模式
dprofile switch coding --target-dir ./my-project/.agent-config
```

---

## 🗃️ 内置 Profile 库

`dprofile` 内置了 25+ 个生产级别的专业人格，已按类别整理：

### 🏗️ 工程与 AI
- `architect`: 架构边界与工程决策。
- `coding`: 直接的代码实现与修复。
- `reviewer`: 风险优先的代码审查。
- `debugger`: 假设驱动的根因分析。
- `ops`: SRE、生产环境与基础设施。
- `ai-infra`: GPU、vLLM、MCP 与推理优化。
- `ml-researcher`: 模型实验与基准测试。

### 📝 内容与设计
- `writer`: 长文创作与编辑。
- `copywriter`: 转化率、标题与清晰表达。
- `social-media`: 平台原生内容（X、小红书、微博）。
- `designer`: UI 系统与视觉设计。

### 🚀 战略与产品
- `product-manager`: 场景模拟、范围划定与 PRD。
- `founder-mode`: 高杠杆判断力与增长。
- `sales`: 说服、演示与跟进。
- `customer-support`: 问题解决与 FAQ 管理。

### 🧠 深度思考与工具
- `slow-thinker`: 深度推理与替代方案。
- `challenger`: 严格的推敲与假设挑战。
- `minimalist`: 极简输出。
- `prompt-engineer`: Agent 工作流与工具路由。
- `executor`: 直接的任务执行。
- `completionist`: 包含测试/文档的完整交付。

---

## 🛠️ 命令详解

| 命令 | 描述 |
| :--- | :--- |
| `dprofile guide` | 说明何时使用 `switch`、`init` 和 `apply`。 |
| `dprofile list` | 列出库中所有可用的人格套装。 |
| `dprofile init` | 为一个或多个 AI 助手安装项目 adapter 文件。 |
| `dprofile apply` | 生成项目 adapter 文件，并可选择激活已验证输出。 |
| `dprofile switch` | 将 Agent 自有配置目录切换至指定人格。 |
| `dprofile show` | 查看当前状态或指定人格的详细信息。 |
| `dprofile diff` | 横向对比两个人格的差异。 |
| `dprofile validate-target` | 验证目标目录是否安全，可进行人格管理。 |

---

## 🤝 开发与发布

### 运行测试
```bash
python3 -m unittest discover -s tests -v
```

### 发布新版本
1. 更新 `pyproject.toml` 和 `agent_profile/__init__.py` 中的版本号。
2. 创建并推送标签：
   ```bash
   git tag v0.1.1
   git push origin main && git push origin v0.1.1
   ```

## 📄 开源协议

MIT
