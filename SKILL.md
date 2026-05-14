---
name: agent-profile
description: Use this skill whenever the user wants an Agent to switch, list, inspect, compare, validate, or manage predefined Agent profiles/personas/workspaces. This includes requests like "switch to architect", "use ops profile", "切到写作人格", "agent-profile switch", or anything involving USER.md, SOUL.md, and AGENTS.md profile sets. The Agent must identify the target Agent configuration directory before switching.
---

# Agent Profile Switcher

This skill manages Agent profiles as complete working persona sets, not as one-off prompts.

The skill directory is the profile library. It is not necessarily the active Agent configuration directory.

A profile is a directory containing:

- `USER.md`: user model, preferences, background, constraints, and communication habits.
- `SOUL.md`: agent identity, voice, values, judgment standards, and output expectations.
- `AGENTS.md`: operating protocol, tool rules, workflow, failure handling, and permission boundaries.
- `manifest.yaml`: profile metadata.

## Agent Workflow

Before switching, identify the target Agent configuration directory.

Use this rule:

1. If the user explicitly provides a directory, use that directory.
2. If the user says "this workspace" or the request is clearly workspace-local, use the workspace root.
3. If the request targets a system-level Agent directory, require the user to provide or confirm the exact path.
4. If the target is ambiguous, ask for the target directory before changing files.

After the target directory is known:

1. Validate that the selected profile exists and contains `USER.md`, `SOUL.md`, `AGENTS.md`, and `manifest.yaml`.
2. Validate that the target directory can safely receive `USER.md`, `SOUL.md`, and `AGENTS.md`.
3. Back up existing target files into `.agent-profile-backups/`.
4. Write the selected profile into the target directory using symlinks by default.
5. Write `.agent-profile-state.json` into the target directory.
6. Report the active profile, target directory, write mode, changed files, and backup path.
7. Do not modify unrelated files.

## CLI

The bundled CLI performs deterministic file operations. The Agent provides the target directory.

```bash
python scripts/agent_profile.py list
python scripts/agent_profile.py list --target-dir /path/to/agent-config

python scripts/agent_profile.py validate-profile architect
python scripts/agent_profile.py validate-target --target-dir /path/to/agent-config

python scripts/agent_profile.py switch architect --target-dir /path/to/agent-config
python scripts/agent_profile.py switch architect --target-dir /path/to/agent-config --mode copy

python scripts/agent_profile.py show --target-dir /path/to/agent-config
python scripts/agent_profile.py show architect

python scripts/agent_profile.py diff architect writer
```

Use `--profiles-dir /path/to/profiles` when the profile library is not this skill's bundled `profiles/` directory.

## Directory Model

```text
agent-profile/
  SKILL.md
  pyproject.toml
  agent_profile/
    cli.py
    profiles/
      architect/
        manifest.yaml
        USER.md
        SOUL.md
        AGENTS.md
  scripts/
    agent_profile.py

target-agent-config/
  USER.md
  SOUL.md
  AGENTS.md
  .agent-profile-state.json
  .agent-profile-backups/
```

## Write Modes

Default to symlink mode:

```bash
python scripts/agent_profile.py switch architect --target-dir /path/to/agent-config
```

Use copy mode when symlinks are inappropriate, such as portable exports, system-level directories, or tools that do not preserve links:

```bash
python scripts/agent_profile.py switch architect --target-dir /path/to/agent-config --mode copy
```

## Profile Semantics

Treat the three files as separate layers:

- Keep user background and preferences in `USER.md`.
- Keep the Agent's identity and style in `SOUL.md`.
- Keep execution rules and tooling protocol in `AGENTS.md`.

Avoid mixing role/personality rules into `AGENTS.md`, and avoid putting workflow/tool instructions into `SOUL.md`.

## Safety

- Never guess a system-level Agent directory.
- Prefer asking for `--target-dir` over probing many product-specific locations.
- Back up existing target files before switching.
- Refuse to replace directories named `USER.md`, `SOUL.md`, or `AGENTS.md`.
- Never remove or rewrite unrelated files.
- If a requested profile or target directory is invalid, stop and report the validation error.
