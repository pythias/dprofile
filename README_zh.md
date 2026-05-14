# dprofile

Agent Profile 切换工具，用于管理 `USER.md`、`SOUL.md` 和 `AGENTS.md` 角色设定集。

`dprofile` 不仅是为人设计的，更是为 Agent（智能体）设计的。它为 Agent 提供了一种安全、确定性的方式，将其目标配置目录切换到预定义的 Profile（配置文件）。

内置的 Profile 库包含在本项目中。目标目录由 Agent 在运行时提供。

## 为什么要用它

现代 Agent 的工作流需要的不仅仅是一个临时的提示词（Prompt）。一个实用的 Agent Profile 通常包含三个独立的层级：

- `USER.md`：Agent 正在帮助谁，包括背景、偏好和约束。
- `SOUL.md`：Agent 应该是谁，包括身份、价值观、语气和标准。
- `AGENTS.md`：Agent 应该如何工作，包括工具、工作流、安全和错误处理。

`dprofile` 将这三个文件视为一个可整体切换的 Profile。

## 安全模型

CLI 工具不会猜测系统级的 Agent 目录。

使用此技能的 Agent 必须首先识别目标配置目录：

- 如果用户提供了路径，则使用该路径。
- 如果用户明确指当前工作区，则使用工作区根目录。
- 如果目标是系统级的 Agent 配置目录，请要求用户提供或确认确切路径。
- 如果目标不明确，请在更改文件前进行确认。

在切换之前，`dprofile` 会将现有的目标文件备份到 `.agent-profile-backups/` 中，并写入 `.agent-profile-state.json` 以便检查当前生效的 Profile。

## 安装

从克隆的仓库安装：

```bash
python3 -m pip install -e .
```

然后运行：

```bash
dprofile list
```

如果不进行安装，可以使用本地包装脚本：

```bash
python3 scripts/agent_profile.py list
```

## 使用模式

`dprofile` 设计了两种主要使用场景：

### 1. Agent 驱动（自动化）
Agent 可以利用此工具自主切换自身或子 Agent 的身份。通过提供目标配置目录，Agent 能够“化身”为库中的任何角色。

```bash
# Agent 的操作指令示例：
# “将我当前在工作区中的人格切换为 'architect'（架构师）。”
dprofile switch architect --target-dir .
```

### 2. 手动 CLI（人工操作）
开发者可以手动管理不同项目中的 Agent 配置。

```bash
# 列出所有可用人格
dprofile list

# 将本地项目的配置切换为 'coding'（编码）模式
dprofile switch coding --target-dir ./my-project/.agent-config
```

## 快速上手

列出内置的 Profile：

```bash
dprofile list
```

将目标 Agent 配置目录切换为 `completionist`（交付专家）：

```bash
dprofile switch completionist --target-dir /path/to/agent-config
```

查看目标目录的当前 Profile 状态：

```bash
dprofile show --target-dir /path/to/agent-config
```

在切换前验证目标目录：

```bash
dprofile validate-target --target-dir /path/to/agent-config
```

对比两个 Profile：

```bash
dprofile diff architect writer
```

## 写入模式

默认情况下，切换使用符号链接（symlink）：

```bash
dprofile switch architect --target-dir /path/to/agent-config
```

对于便携式导出、系统级目录或不支持符号链接的工具，请使用复制模式：

```bash
dprofile switch architect --target-dir /path/to/agent-config --mode copy
```

## 自定义 Profile 库

使用 `--profiles-dir` 指向另一个 Profile 库：

```bash
dprofile list --profiles-dir /path/to/profiles
dprofile switch ops --profiles-dir /path/to/profiles --target-dir /path/to/agent-config
```

每个 Profile 目录必须包含：

```text
manifest.yaml
USER.md
SOUL.md
AGENTS.md
```

## 内置 Profile 列表

- `architect`: 架构设计、工程决策、AI 基础设施。
- `coding`: 直接开发实现与修复。
- `reviewer`: 代码审查与风险优先的反思。
- `debugger`: 基于假设的调试。
- `ops`: SRE 与生产运维。
- `prompt-engineer`: 提示词、Agent、工作流、工具路由。
- `data-analyst`: SQL、指标、仪表盘与趋势分析。
- `ml-researcher`: 模型实验、基准测试与论文。
- `ai-infra`: 推理架构、GPU、vLLM、MCP 与 Agent 运行时。
- `writer`: 长文撰写与编辑。
- `copywriter`: 标题、标语、转化率与情绪引导。
- `social-media`: 小红书、Twitter/X、微博、Threads 等渠道原生内容。
- `designer`: UI 风格、视觉系统与信息设计。
- `product-manager`: PRD、用户场景、范围划定与指标。
- `founder-mode`: 战略、优先级、增长与判断力。
- `sales`: 说服、演示、异议处理与商务跟进。
- `customer-support`: 支撑回复、投诉处理、FAQ 与问题解决。
- `teacher`: 循序渐进的教学与类比驱动的解释。
- `travel-planner`: 行程、酒店、节奏与旅行约束。
- `fitness-coach`: 训练、营养、恢复与进度管理。
- `minimalist`: 极简输出。
- `challenger`: 严格的推敲与假设挑战。
- `slow-thinker`: 深度思考、替代方案与权衡分析。
- `executor`: 直接的任务执行。
- `completionist`: 包含测试、文档和清理的完整交付。

## 命令详解

```bash
dprofile list [--profiles-dir DIR] [--target-dir DIR]
dprofile validate-profile [PROFILE] [--profiles-dir DIR]
dprofile validate-target --target-dir DIR
dprofile switch PROFILE --target-dir DIR [--profiles-dir DIR] [--mode symlink|copy]
dprofile show [PROFILE] [--target-dir DIR] [--profiles-dir DIR]
dprofile diff LEFT RIGHT [--profiles-dir DIR]
```

为了保持兼容性，同时也安装了旧版命令名 `agent-profile`。

---

## 开发者指南

### 开发调试

运行测试：

```bash
python3 -m unittest discover -s tests -v
```

验证内置 Profile 的合法性：

```bash
python3 scripts/agent_profile.py validate-profile
```

### 发布流程

版本发布通过 GitHub Actions 使用 PyPI Trusted Publishing 自动完成。这避免了在 GitHub Secrets 中存储 PyPI API Token。

在 PyPI 项目中配置 Publisher：

```text
Owner: pythias
Repository name: dprofile
Workflow name: publish.yml
Environment name: pypi
```

发布步骤：更新 `pyproject.toml` 和 `agent_profile/__init__.py` 中的版本号，提交并打上标签：

```bash
git tag v0.1.1
git push origin main
git push origin v0.1.1
```

"Publish to PyPI" 工作流将自动运行测试、验证 Profile、构建分发包、执行 `twine check` 并上传至 PyPI。

## 开源协议

MIT
