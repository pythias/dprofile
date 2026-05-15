# 🎭 dprofile

[![PyPI version](https://img.shields.io/pypi/v/dprofile.svg?maxAge=0)](https://pypi.org/project/dprofile/)
[![Python versions](https://img.shields.io/pypi/pyversions/dprofile.svg?maxAge=0)](https://pypi.org/project/dprofile/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?maxAge=0)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/pythias/dprofile/actions/workflows/ci.yml/badge.svg?maxAge=0)](https://github.com/pythias/dprofile/actions/workflows/ci.yml)

**Instant Persona Switching for AI Agents.**

`dprofile` is a safe, deterministic profile switcher designed for the modern Agent era. It treats persona sets (`USER.md`, `SOUL.md`, `AGENTS.md`) as atomic units, allowing both humans and AI Agents to swap identities in milliseconds.

`SKILL.md` is the primary Agent interface for this project. It defines the workflow and safety rules. The CLI is the secondary deterministic executor and fallback guide.

[中文版 (Chinese Version)](README_zh.md)

---

## ✨ Key Features

- **🤖 Agent-Native**: Designed to be called by Agents to self-evolve or switch sub-agent configurations.
- **🛡️ Safety First**: Automatic backups, `.dprofile/` state, and validation of target directories.
- **🏗️ The Three-Layer Model**:
    - `USER.md`: Who you are helping (Background & Preferences).
    - `SOUL.md`: Who you are (Identity & Values).
    - `AGENTS.md`: How you work (Tools & Protocols).
- **📄 Adapter activation**: Verified adapters get a rendered copy at each tool's native paths.

## 🚀 Quick Start

Start by installing the Agent skill. In your Agent, ask:

```text
Install the dprofile skill from github.com/pythias/dprofile.
```

After the skill is installed, ask the Agent to use a profile:

```text
Use the coding profile for this project with Claude.
```

The Agent should read `SKILL.md`, classify the target, and choose the correct operation. For code projects, that usually means applying adapter files through `dprofile apply`.

The CLI is optional but recommended for deterministic execution:

```bash
pip install dprofile -i https://pypi.org/simple
```

---

## 📖 Usage Patterns

### 1. Global Agent Configs
Agents use `dprofile` to configure their standard global identities.

```bash
# Agent instruction: "Configure my global Claude persona to 'architect'."
dprofile apply architect --ai claude -g
```

### 2. Code Projects
Code projects may be opened by many Agents and IDEs, so `dprofile` targets the current project by default.

It generates and activates Agent-specific files such as `CLAUDE.md`, `.cursor/rules/dprofile.mdc`, `.github/copilot-instructions.md`, `GEMINI.md`, or `AGENTS.md`.

Adapters do not all receive the same source layers. Claude and Gemini get the full profile context, while Cursor, Copilot, Codex, and OpenCode default to the operating protocol layer so project instructions stay focused.

```bash
# Apply profile to the current project for Claude and Cursor
dprofile apply coding --ai claude,cursor

# Apply to all verified adapters in the current project
dprofile apply coding --ai all
```

---

## 🗃️ Bundled Profiles

`dprofile` comes with 25+ production-ready personas categorized for quick access:

### 🏗️ Engineering & AI
- `architect`: System boundaries and engineering decisions.
- `coding`: Direct implementation and fixes.
- `reviewer`: Risk-first feedback and code quality.
- `debugger`: Hypothesis-driven root cause analysis.
- `ops`: SRE, production, and infrastructure.
- `ai-infra`: GPUs, vLLM, MCP, and inference optimization.
- `ml-researcher`: Model experiments and benchmarks.
- `linux-expert`: Kernel, syscalls, and low-level system mastery.

### 📝 Content & Design
- `writer`: Long-form content and editing.
- `copywriter`: Conversion, headlines, and clarity.
- `social-media`: Platform-native posts (X, Red, Weibo).
- `designer`: UI systems and visual design.

### 🚀 Strategy & Product
- `product-manager`: Scenarios, scope, and PRDs.
- `founder-mode`: High-leverage judgment and growth.
- `sales`: Persuasion, demos, and follow-ups.
- `customer-support`: Resolution and FAQ management.

### 🧠 Critical Thinking & Utility
- `slow-thinker`: Deep reasoning and alternatives.
- `challenger`: Rigorous pushback and assumption testing.
- `minimalist`: Extreme conciseness.
- `prompt-engineer`: Agent workflows and tool routing.
- `executor`: Direct task execution.
- `completionist`: End-to-end delivery with tests/docs.

---

## 🛠️ Commands

| Command | Description |
| :--- | :--- |
| `dprofile list` | Lists profiles in the library. `*` reflects `.dprofile/state.json` in the **current directory** only; use `show -g` for global Agent homes. |
| `dprofile apply` | Apply a profile to the project or global Agent config. |
| `dprofile show` | Inspect current state or a specific profile. |
| `dprofile diff` | Compare two profiles side-by-side. |
| `dprofile guide` | Detailed usage protocol and adapter info. |
| `dprofile validate-profile` | Validate the structure of a profile. |

---

## 🤝 Development & Release

### Testing
```bash
python3 -m unittest discover -s tests -v
```

### Publishing a Release
1. Update version in `pyproject.toml` and `dprofile/__init__.py`.
2. Tag and push (use the **same version** as in `pyproject.toml`):

```bash
git tag vX.Y.Z
git push origin main && git push origin vX.Y.Z
```

Replace `X.Y.Z` with the version you set in `pyproject.toml` (for example `0.4.0`, tag as `v0.4.0`).

## 📄 License

MIT
