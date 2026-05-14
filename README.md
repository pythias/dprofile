# 🎭 dprofile

[![PyPI version](https://img.shields.io/pypi/v/dprofile.svg)](https://pypi.org/project/dprofile/)
[![Python versions](https://img.shields.io/pypi/pyversions/dprofile.svg)](https://pypi.org/project/dprofile/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/pythias/dprofile/actions/workflows/ci.yml/badge.svg)](https://github.com/pythias/dprofile/actions/workflows/ci.yml)

**Instant Persona Switching for AI Agents.**

`dprofile` is a safe, deterministic profile switcher designed for the modern Agent era. It treats persona sets (`USER.md`, `SOUL.md`, `AGENTS.md`) as atomic units, allowing both humans and AI Agents to swap identities in milliseconds.

[中文版 (Chinese Version)](README_zh.md)

---

## ✨ Key Features

- **🤖 Agent-Native**: Designed to be called by Agents to self-evolve or switch sub-agent configurations.
- **🛡️ Safety First**: Automatic backups, state tracking, and validation of target directories.
- **🏗️ The Three-Layer Model**:
    - `USER.md`: Who you are helping (Background & Preferences).
    - `SOUL.md`: Who you are (Identity & Values).
    - `AGENTS.md`: How you work (Tools & Protocols).
- **🔗 Hybrid Modes**: Switch via **Symlinks** (for live updates) or **Copy** (for portable exports).

## 🚀 Install

```bash
pip install dprofile
```

---

## 📖 Usage Patterns

### 1. Agent-Driven (Automation)
Agents use `dprofile` to autonomously switch their own identity or configure specialized workers.

```bash
# Agent instruction: "Switch my persona to 'architect' in the current workspace."
dprofile switch architect --target-dir .
```

### 2. Manual CLI (Human)
Developers can manage agent personas across projects with zero friction.

```bash
# List all available personas
dprofile list

# Switch a local project config to 'coding' mode
dprofile switch coding --target-dir ./my-project/.agent-config
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
| `dprofile list` | List all available profiles in the library. |
| `dprofile switch` | Switch target directory to a specific profile. |
| `dprofile show` | Inspect current state or a specific profile. |
| `dprofile diff` | Compare two profiles side-by-side. |
| `dprofile validate-target` | Ensure a directory is safe for profile management. |

---

## 🤝 Development & Release

### Testing
```bash
python3 -m unittest discover -s tests -v
```

### Publishing a Release
1. Update version in `pyproject.toml` and `agent_profile/__init__.py`.
2. Create and push a tag:
   ```bash
   git tag v0.1.1
   git push origin main && git push origin v0.1.1
   ```

## 📄 License

MIT
