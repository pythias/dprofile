# 🎭 dprofile

[![PyPI version](https://img.shields.io/pypi/v/dprofile.svg)](https://pypi.org/project/dprofile/)
[![Python versions](https://img.shields.io/pypi/pyversions/dprofile.svg)](https://pypi.org/project/dprofile/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/pythias/dprofile/actions/workflows/ci.yml/badge.svg)](https://github.com/pythias/dprofile/actions/workflows/ci.yml)

**为 AI Agent 量身定制的人格套装切换工具。**

`dprofile` 是一个安全、确定性的人格切换工具，专为现代 Agent 时代设计。它将 `USER.md`、`SOUL.md` 和 `AGENTS.md` 视为一个原子化的“人格套装”，让开发者和 Agent 都能在毫秒间完成身份切换。

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

## 🚀 快速安装

```bash
pip install dprofile
```

---

## 📖 使用模式

### 1. Agent 驱动（自动化）
Agent 利用 `dprofile` 自主切换身份或配置专门的协作节点。

```bash
# Agent 操作指令示例：“将我当前工作区的人格切换为 'architect'（架构师）。”
dprofile switch architect --target-dir .
```

### 2. 手动 CLI（人工操作）
开发者可以无缝管理不同项目中的 Agent 人格设定。

```bash
# 列出所有可用人格
dprofile list

# 将本地项目的配置切换为 'coding'（编码）模式
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
| `dprofile list` | 列出库中所有可用的人格套装。 |
| `dprofile switch` | 将目标目录切换至指定人格。 |
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
