---
name: dprofile
description: Use this skill whenever the user wants an Agent to apply, list, inspect, compare, validate, or manage predefined Agent profiles/personas/workspaces across coding agents and IDEs. This includes requests like "apply architect profile", "use ops profile", "切到写作人格", "dprofile apply", or anything involving USER.md, SOUL.md, AGENTS.md, SKILL.md, or IDE-specific agent instruction files. The Agent must classify the target as either an Agent-owned configuration directory or a code project before changing files.
---

# dprofile

This skill manages Agent profiles as complete working persona sets, not as one-off prompts.

This `SKILL.md` is the primary interface for Agent behavior. It defines judgment, target classification, adapter selection, and safety policy. The `dprofile` CLI is secondary: it is a deterministic executor for professional users, scripts, and Agents that need command help when the skill is not installed.

The skill directory is the profile library. It is not necessarily the active Agent configuration directory, and it is not necessarily a code project that should receive generated files.

A profile is a source package containing:

- `USER.md`: user model, preferences, background, constraints, and communication habits.
- `SOUL.md`: agent identity, voice, values, judgment standards, and output expectations.
- `AGENTS.md`: operating protocol, tool rules, workflow, failure handling, and permission boundaries.
- `manifest.yaml`: profile metadata.

Treat these files as dprofile's internal source format. Do not assume every Agent, IDE, or code project should receive these exact filenames.

## Target Classification

Before changing files, classify the target:

1. **Agent config target**: a directory owned by a specific Agent runtime or profile system, such as a Codex, Claude, Gemini, or other Agent configuration directory.
2. **Code project target**: an application, library, repo, workspace, or other code directory that may be opened by many different Agents and IDEs.

Rules:

1. If the user asks to configure "this Agent", "my Agent", or a named Agent's own profile, treat the target as a global Agent target. Use `apply -g`.
2. If the user says "this repo", "this project", "workspace", or points at source code, treat the target as a local project target. Use `apply`.
3. If the target is ambiguous, ask one concise clarifying question before changing files.

## Unified Workflow: `apply`

The `apply` command handles Agent configs and code projects: it writes `.dprofile/generated/<adapter>/...` for every requested adapter, then activates verified adapters onto their native paths (see Activation Policy for shared-path rules).

1. Validate the profile.
2. Select adapters via `--ai`.
3. **Local** (default): current directory. **Global** (`-g`): standard homes such as `~/.claude`.

```bash
dprofile apply linux-expert --ai claude -g
dprofile apply coding --ai claude,cursor
dprofile apply coding --ai all --force
```

The Agent chooses local vs `-g` from target classification (`Target Classification` above).

## Adapter Registry

Adapters convert dprofile's source package into an Agent or IDE's native instruction format.

Adapter status:

- `verified`: the output path and load behavior are known from official docs, local docs, or existing project conventions.
- `project-root`: activation writes a root-level project instruction file.
- `scoped`: activation writes inside a tool-specific directory.
- `generated-only`: dprofile can generate guidance, but should not activate it automatically.

Verified adapters:

| Adapter | Generated output | Activated output | Source layers | Status |
| --- | --- | --- | --- | --- |
| `claude` | `.dprofile/generated/claude/CLAUDE.md` | `CLAUDE.md` | `USER.md`, `SOUL.md`, `AGENTS.md` | verified, project-root |
| `cursor` | `.dprofile/generated/cursor/dprofile.mdc` | `.cursor/rules/dprofile.mdc` | `AGENTS.md` | verified, scoped |
| `copilot` | `.dprofile/generated/copilot/copilot-instructions.md` | `.github/copilot-instructions.md` | `AGENTS.md` | verified, scoped |
| `codex` | `.dprofile/generated/codex/AGENTS.md` | `AGENTS.md` | `AGENTS.md` with profile summary | verified, project-root |
| `gemini` | `.dprofile/generated/gemini/GEMINI.md` | `GEMINI.md` | `USER.md`, `SOUL.md`, `AGENTS.md` | verified, project-root |
| `opencode` | `.dprofile/generated/opencode/AGENTS.md` | `AGENTS.md` | `AGENTS.md` with profile summary | verified, project-root |

Unverified or project-dependent adapters:

```text
agent
augment
codebuddy
continue
droid
hermes
kilocode
kiro
openclaw
qoder
roocode
trae
warp
windsurf
```

For an unverified adapter, write only:

```text
.dprofile/generated/<adapter>/INSTRUCTIONS.md
```

The generated file may include all three source layers, but it must say manual activation is required. Then report that activation requires local or official path verification. Do not guess paths like `.augment/`, `.warp/`, or `.trae/` unless the user provides documentation or the project already contains the convention.

## Adapter Content Rules

Different Agents do not support the three dprofile source files equally.

Use these content rules:

- `claude` and `gemini`: full context adapters. Include `USER.md`, `SOUL.md`, and `AGENTS.md` because their native project memory files are broad Markdown context files.
- `cursor`: project rule adapter. Emit MDC frontmatter and include only `AGENTS.md` by default. Do not place full user/persona context into Cursor project rules unless the user asks.
- `copilot`: project instruction adapter. Include only `AGENTS.md` by default because Copilot project instructions should stay focused on coding behavior and repository rules.
- `codex` and `opencode`: AGENTS.md-compatible adapters. Include a short active-profile summary and the `AGENTS.md` operating protocol. Do not dump full `USER.md` or `SOUL.md` into project-root `AGENTS.md` by default.
- unverified adapters: generated-only manual instructions. Include all layers for human review, but do not activate automatically.

## Activation Policy

The `apply` command always:

1. Writes each adapter's output under `.dprofile/generated/<adapter>/...`.
2. **Activates** verified adapters (writes or overwrites their native paths in the target directory). Unverified adapters stay generate-only and are listed under `skipped_activation` in state.

If multiple adapters share one native activation path (e.g. both `codex` and `opencode` write `AGENTS.md`), **the first adapter listed in `--ai` wins** for that path: the file receives that adapter's rendered content. Later adapters keep their `.dprofile/generated/` output but do not overwrite the shared path again. The CLI prints this outcome; `skipped_duplicate_activation` in state lists `skipped`, `path`, and `active` (winner).

All generated or activated files should include a short managed marker when the target format allows comments:

```text
<!-- dprofile-managed: true; profile=<name>; adapter=<adapter> -->
```

If the format does not support comments, record ownership in `.dprofile/state.json`.

## CLI

The bundled CLI performs deterministic file operations. It is intended for professional users and automation. It also exposes concise fallback guidance through `dprofile --help`, `dprofile apply --help`, and `dprofile guide`.

The Agent remains responsible for target classification, adapter selection, and safety checks. Prefer this `SKILL.md` for Agent behavior, then use the CLI to execute the chosen operation.

Use CLI commands only after deciding whether the target is an Agent config target or a code project target.

For Agent config targets (Global):

```bash
dprofile list
dprofile validate-profile architect
dprofile apply architect --ai claude -g
dprofile show -g --ai claude
dprofile diff architect writer
```

Use `list` knowing the active profile marker uses `.dprofile/state.json` in the **current directory** only (`dprofile list --help`). For global installs, prefer `show -g --ai <adapter>`.

For code project targets:

```bash
dprofile apply architect --ai codex
dprofile apply architect --ai claude,cursor,copilot
dprofile apply architect --ai all
dprofile apply architect --ai all --force
```

## Profile Semantics

Treat the three source files as separate layers:

- Keep user background and preferences in `USER.md`.
- Keep the Agent's identity and style in `SOUL.md`.
- Keep execution rules and tooling protocol in `AGENTS.md`.

When generating an adapter file, merge the layers in this order unless the adapter has a stronger native convention:

1. Profile metadata from `manifest.yaml`.
2. User context from `USER.md`.
3. Agent identity from `SOUL.md`.
4. Operating rules from `AGENTS.md`.
5. Adapter-specific notes.

Avoid mixing role/personality rules into project-only `AGENTS.md` files unless the user is explicitly configuring that Agent for the project.

## Safety

- Never guess a system-level Agent directory. Use `-g` for standard paths.
- Existing unmanaged activated files are skipped unless `--force` (after backup for managed overwrites).
- Back up existing target files before replacing managed or forced overwrites.
- Refuse to replace directories named `USER.md`, `SOUL.md`, `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`.
- Never remove or rewrite unrelated files.
- If a requested profile or adapter is invalid, stop and report the validation error.
