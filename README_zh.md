# 🎭 dprofile

[![PyPI version](https://img.shields.io/pypi/v/dprofile.svg?maxAge=0)](https://pypi.org/project/dprofile/)
[![Python versions](https://img.shields.io/pypi/pyversions/dprofile.svg?maxAge=0)](https://pypi.org/project/dprofile/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?maxAge=0)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/pythias/dprofile/actions/workflows/ci.yml/badge.svg?maxAge=0)](https://github.com/pythias/dprofile/actions/workflows/ci.yml)

**为 AI Agent 量身定制的人格套装切换工具。**

`dprofile` 是一个安全、确定性的人格切换工具，专为现代 Agent 时代设计。它将 `USER.md`、`SOUL.md` 和 `AGENTS.md` 视为一个原子化的“人格套装”，让开发者和 Agent 都能在毫秒间完成身份切换。

本项目以 `SKILL.md` 作为 Agent 的主入口，负责定义工作流和安全规则。CLI 是次级的确定性执行器，也提供无 skill 场景下的 fallback 指南。

[English Version](README.md)

---

## ✨ 核心特性

- **🤖 Agent 原生设计**：支持 Agent 自主调用以进化自身身份或配置子 Agent 任务。
- **🛡️ 安全第一**：自动备份、`.dprofile/` 下状态，以及对目标目录的校验。
- **🏗️ 三层人格模型**：
    - `USER.md`：你正在帮助谁（用户背景与偏好）。
    - `SOUL.md`：你是谁（身份认同与价值观）。
    - `AGENTS.md`：你如何工作（工具协议与工作流）。
- **📄 适配器激活**：已验证的适配器会在各工具约定路径写入渲染后的副本。

## 🚀 快速开始

先安装 Agent skill。在你的 Agent 里直接说：

```text
从 github.com/pythias/dprofile 安装 dprofile skill。
```

安装 skill 后，让 Agent 使用某个 profile：

```text
在这个项目里用 Claude 使用 coding profile。
```

Agent 应该读取 `SKILL.md`，判断目标类型，然后选择正确操作。对代码项目来说，通常会通过 `dprofile apply` 生成并激活 adapter 文件。

CLI 是可选项，但建议安装，方便确定性执行：

```bash
pip install dprofile -i https://pypi.org/simple
```

---

## 📖 使用模式

### 1. 全局 Agent 配置
Agent 利用 `dprofile` 在其标准全局路径中配置身份。

```bash
# Agent 操作指令示例：“将我的全局 Claude 人格切换为 'architect'（架构师）。”
dprofile apply architect --ai claude -g
```

### 2. 代码项目
代码项目可能同时被多种 Agent 和 IDE 打开，因此 `dprofile` 默认针对当前目录进行操作。

它会自动生成并激活具体 Agent 的原生文件，例如 `CLAUDE.md`、`.cursor/rules/dprofile.mdc`、`.github/copilot-instructions.md`、`GEMINI.md` 或 `AGENTS.md`。

不同 adapter 会拿到不同层级的上下文。Claude 和 Gemini 使用完整 profile 上下文；Cursor、Copilot、Codex、OpenCode 默认只使用操作协议层。

```bash
# 为当前项目的 Claude 和 Cursor 应用人格
dprofile apply coding --ai claude,cursor

# 为当前项目所有已验证的适配器应用人格
dprofile apply coding --ai all
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
- `linux-expert`: 内核、系统调用与底层系统精通。

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
| `dprofile list` | 列出库中的人格；`*` 仅反映**当前目录**下 `.dprofile/state.json`，全局请看 `show -g`。 |
| `dprofile apply` | 将人格应用至当前项目或全局 Agent 配置。 |
| `dprofile show` | 查看当前状态或指定人格的详细信息。 |
| `dprofile diff` | 横向对比两个人格的差异。 |
| `dprofile guide` | 详细的使用协议与适配器信息。 |
| `dprofile validate-profile` | 校验 profile 结构是否正确。 |

---

## 🤝 开发与发布

### 运行测试
```bash
python3 -m unittest discover -s tests -v
```

### 发布新版本
1. 更新 `pyproject.toml` 和 `dprofile/__init__.py` 中的版本号。
2. 打标签并推送（标签版本需与 `pyproject.toml` 一致）：

   ```bash
   git tag vX.Y.Z
   git push origin main && git push origin vX.Y.Z
   ```

   将 `X.Y.Z` 换成你在 `pyproject.toml` 中写的版本号（例如版本为 `0.4.0` 时使用标签 `v0.4.0`）。

## 📄 开源协议

MIT
