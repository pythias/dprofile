# dprofile

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
agent-profile list
```

Without installing, use the local wrapper:

```bash
python3 scripts/agent_profile.py list
```

## Quick Start

List bundled profiles:

```bash
agent-profile list
```

Switch a target Agent config directory to `completionist`:

```bash
agent-profile switch completionist --target-dir /path/to/agent-config
```

Show the active profile for a target directory:

```bash
agent-profile show --target-dir /path/to/agent-config
```

Validate the target directory before switching:

```bash
agent-profile validate-target --target-dir /path/to/agent-config
```

Compare two profiles:

```bash
agent-profile diff architect writer
```

## Write Modes

By default, switching uses symlinks:

```bash
agent-profile switch architect --target-dir /path/to/agent-config
```

Use copy mode for portable exports, system-level directories, or tools that do not preserve symlinks:

```bash
agent-profile switch architect --target-dir /path/to/agent-config --mode copy
```

## Custom Profile Library

Use `--profiles-dir` to point at another profile library:

```bash
agent-profile list --profiles-dir /path/to/profiles
agent-profile switch ops --profiles-dir /path/to/profiles --target-dir /path/to/agent-config
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
- `writer`: long-form writing and editing.
- `prompt-engineer`: prompts, Agents, workflows, tool routing.
- `minimalist`: concise output.
- `challenger`: rigorous pushback and assumption testing.
- `executor`: direct task execution.
- `completionist`: complete delivery with tests, docs, and cleanup.

## Commands

```bash
agent-profile list [--profiles-dir DIR] [--target-dir DIR]
agent-profile validate-profile [PROFILE] [--profiles-dir DIR]
agent-profile validate-target --target-dir DIR
agent-profile switch PROFILE --target-dir DIR [--profiles-dir DIR] [--mode symlink|copy]
agent-profile show [PROFILE] [--target-dir DIR] [--profiles-dir DIR]
agent-profile diff LEFT RIGHT [--profiles-dir DIR]
```

## Development

Run tests:

```bash
python3 -m unittest tests/test_agent_profile.py -v
```

Validate bundled profiles:

```bash
python3 scripts/agent_profile.py validate-profile
```

## License

MIT
