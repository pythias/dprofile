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

### 🏗️ 工程与 AI
- `architect`: 架构边界与工程决策。**推荐人群**：主导工程师、系统架构师。
- `coding`: 直接的代码实现与修复。**推荐人群**：开发人员、个人贡献者。
- `reviewer`: 风险优先的代码审查。**推荐人群**：代码审核者、质量把控者。
- `debugger`: 假设驱动的根因分析。**推荐人群**：问题排查专家、运维工程师。
- `ops`: SRE、生产环境与基础设施。**推荐人群**：运维专家、平台工程师。
- `ai-infra`: GPU、vLLM、MCP 与推理优化。**推荐人群**：AI 基础设施工程师。
- `ml-researcher`: 模型实验与基准测试。**推荐人群**：数据科学家、算法工程师。

### 📝 内容与设计
- `writer`: 长文创作与编辑。**推荐人群**：博主、文档撰写者。
- `copywriter`: 转化率、标题与清晰表达。**推荐人群**：市场营销人员、增长黑客。
- `social-media`: 平台原生内容（X、小红书、微博）。**推荐人群**：社媒运营。
- `designer`: UI 系统与视觉设计。**推荐人群**：产品设计师、UI/UX 工程师。

### 🚀 战略与产品
- `product-manager`: 场景模拟、范围划定与 PRD。**推荐人群**：产品经理、产品负责人。
- `founder-mode`: 高杠杆判断力与增长。**推荐人群**：创始人、技术负责人。
- `sales`: 说服、演示与跟进。**推荐人群**：售前工程师、客户经理。
- `customer-support`: 问题解决与 FAQ 管理。**推荐人群**：客服主管、社区经理。

### 🎓 教育与生活
- `teacher`: 循序渐进的类比式教学。**推荐人群**：教育工作者、导师。
- `travel-planner`: 行程规划与约束处理。**推荐人群**：旅行爱好者。
- `fitness-coach`: 训练、恢复与营养建议。**推荐人群**：运动员、健身爱好者。

### 🧠 深度思考与工具
- `slow-thinker`: 深度推理与替代方案。**推荐人群**：战略规划者、研究员。
- `challenger`: 严格的推敲与假设挑战。**推荐人群**：评审人员、同行评议者。
- `minimalist`: 极简输出。**推荐人群**：快速状态更新、资深用户。
- `prompt-engineer`: Agent 工作流与工具路由。**推荐人群**：LLM 开发者。
- `executor`: 直接的任务执行。**推荐人群**：任务导向型工作流。
- `completionist`: 包含测试/文档的完整交付。**推荐人群**：高质量 PR 提交者。

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
