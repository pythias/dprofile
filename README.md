# dprofile

[中文版 (Chinese Version)](README_zh.md)

Agent Profile Switcher for `USER.md`, `SOUL.md`, and `AGENTS.md` persona sets.

`dprofile` is built for Agents, not just humans. It gives an Agent a safe, deterministic way to switch a target Agent configuration directory to a predefined profile.

The profile library lives in this project. The target directory is provided by the Agent at runtime.

## Why

Modern Agent workflows need more than a temporary prompt. A useful Agent profile usually has three separate layers:

- `USER.md`: who the Agent is helping, including background, preferences, and constraints.
- `SOUL.md`: who the Agent should be, including identity, values, voice, and standards.
- `AGENTS.md`: how the Agent should work, including tools, workflow, safety, and failure handling.

`dprofile` treats those three files as one switchable profile.

## Safety Model

The CLI does not guess system-level Agent directories.

The Agent using this skill must identify the target configuration directory first:

- If the user provides a path, use that path.
- If the user clearly means the current workspace, use the workspace root.
- If the target is a system-level Agent config directory, ask the user to provide or confirm the exact path.
- If the target is ambiguous, ask before changing files.

Before switching, `dprofile` backs up existing target files into `.agent-profile-backups/` and writes `.agent-profile-state.json` so the active profile is inspectable.

## Install

From a clone:

```bash
python3 -m pip install -e .
```

Then:

```bash
dprofile list
```

Without installing, use the local wrapper:

```bash
python3 scripts/agent_profile.py list
```

## Usage Patterns

`dprofile` is designed for two primary scenarios:

### 1. Agent-Driven (Automation)
Agents can use this tool to autonomously switch their own identity or the identity of a sub-agent. By providing the target configuration directory, the Agent can "become" any profile in the library.

```bash
# Example instruction for an Agent:
# "Switch my current persona to 'architect' in the current workspace."
dprofile switch architect --target-dir .
```

### 2. Manual CLI (Human)
Developers can manually manage agent configurations across different projects.

```bash
# List available personas
dprofile list

# Switch a local project config to 'coding' mode
dprofile switch coding --target-dir ./my-project/.agent-config
```

## Quick Start

List bundled profiles:

```bash
dprofile list
```

Switch a target Agent config directory to `completionist`:

```bash
dprofile switch completionist --target-dir /path/to/agent-config
```

Show the active profile for a target directory:

```bash
dprofile show --target-dir /path/to/agent-config
```

Validate the target directory before switching:

```bash
dprofile validate-target --target-dir /path/to/agent-config
```

Compare two profiles:

```bash
dprofile diff architect writer
```

## Write Modes

By default, switching uses symlinks:

```bash
dprofile switch architect --target-dir /path/to/agent-config
```

Use copy mode for portable exports, system-level directories, or tools that do not preserve symlinks:

```bash
dprofile switch architect --target-dir /path/to/agent-config --mode copy
```

## Custom Profile Library

Use `--profiles-dir` to point at another profile library:

```bash
dprofile list --profiles-dir /path/to/profiles
dprofile switch ops --profiles-dir /path/to/profiles --target-dir /path/to/agent-config
```

Each profile directory must contain:

```text
manifest.yaml
USER.md
SOUL.md
AGENTS.md
```

## Bundled Profiles

- `architect`: architecture, engineering decisions, AI infrastructure.
- `coding`: direct implementation and fixes.
- `reviewer`: code review and risk-first feedback.
- `debugger`: hypothesis-driven debugging.
- `ops`: SRE and production operations.
- `prompt-engineer`: prompts, Agents, workflows, tool routing.
- `data-analyst`: SQL, metrics, dashboards, and trends.
- `ml-researcher`: model experiments, benchmarks, and papers.
- `ai-infra`: inference architecture, GPUs, vLLM, MCP, and Agent runtimes.
- `writer`: long-form writing and editing.
- `copywriter`: headlines, slogans, conversion, and emotional clarity.
- `social-media`: Xiaohongshu, Twitter/X, Weibo, Threads, and channel-native posts.
- `designer`: UI style, visual systems, and information design.
- `product-manager`: PRDs, user scenarios, scope, and metrics.
- `founder-mode`: strategy, prioritization, growth, and judgment.
- `sales`: persuasion, demos, objections, and business follow-up.
- `customer-support`: support replies, complaints, FAQ, and resolution.
- `teacher`: step-by-step teaching and analogy-driven explanations.
- `travel-planner`: itinerary, hotels, pacing, and travel constraints.
- `fitness-coach`: training, nutrition, recovery, and progression.
- `minimalist`: concise output.
- `challenger`: rigorous pushback and assumption testing.
- `slow-thinker`: deeper reasoning, alternatives, and tradeoff analysis.
- `executor`: direct task execution.
- `completionist`: complete delivery with tests, docs, and cleanup.

## Commands

```bash
dprofile list [--profiles-dir DIR] [--target-dir DIR]
dprofile validate-profile [PROFILE] [--profiles-dir DIR]
dprofile validate-target --target-dir DIR
dprofile switch PROFILE --target-dir DIR [--profiles-dir DIR] [--mode symlink|copy]
dprofile show [PROFILE] [--target-dir DIR] [--profiles-dir DIR]
dprofile diff LEFT RIGHT [--profiles-dir DIR]
```

The legacy command name `agent-profile` is also installed for compatibility.

## Development

Run tests:

```bash
python3 -m unittest tests/test_agent_profile.py -v
```

Validate bundled profiles:

```bash
python3 scripts/agent_profile.py validate-profile
```

## Release

Releases are published by GitHub Actions with PyPI Trusted Publishing. This avoids storing a PyPI API token in GitHub secrets.

Configure the PyPI project publisher with:

```text
Owner: pythias
Repository name: dprofile
Workflow name: publish.yml
Environment name: pypi
```

Then bump the version in `pyproject.toml` and `agent_profile/__init__.py`, commit, tag, and push:

```bash
git tag v0.1.1
git push origin main
git push origin v0.1.1
```

The `Publish to PyPI` workflow will run tests, validate bundled profiles, build the source and wheel distributions, run `twine check`, and upload to PyPI.

## License

MIT
