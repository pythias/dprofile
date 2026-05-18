---
name: dprofile
description: Use this skill whenever the user wants an Agent to apply, list, inspect, compare, validate, or manage predefined Agent profiles/personas/workspaces across coding agents and IDEs. This includes requests like "apply architect profile", "use ops profile", "切到写作人格", "dprofile apply", or anything involving USER.md, SOUL.md, AGENTS.md, SKILL.md, or IDE-specific agent instruction files. The Agent must pick an install target using the three-tier rule (workspace first, then user code directory, then global home) before changing files.
---

# dprofile

This skill manages Agent profiles as complete working persona sets, not as one-off prompts.

This `SKILL.md` is the primary interface for Agent behavior. It defines judgment, target classification, adapter selection, and safety policy. The deterministic file runner is secondary: **`dprofile` CLI** when installed (`pip`), or **`python scripts/dprofile.py`** from the cloned repo root when not — cloning the repo is enough; do not insist on installing a separate CLI for skill-only workflows.

The skill directory is the profile library. It is not necessarily the active Agent configuration directory, and it is not necessarily a code project that should receive generated files.

A profile is a source package containing:

- `USER.md`: user model, preferences, background, constraints, and communication habits.
- `SOUL.md`: agent identity, voice, values, judgment standards, and output expectations.
- `AGENTS.md`: operating protocol, tool rules, workflow, failure handling, and permission boundaries.
- `manifest.yaml`: profile metadata.

Treat these files as dprofile's internal source format. Do not assume every Agent, IDE, or code project should receive these exact filenames.

## Install target: three tiers

Before `apply`, decide **which directory is the install root**. The runner writes `.dprofile/` and native adapter files **relative to that directory**. Pick the **highest tier that applies**; do not skip to a lower tier without a reason.

| Priority | Tier | When to use | How to run |
| --- | --- | --- | --- |
| 1 | **Workspace** | The tool has a dedicated workspace root (OpenClaw workspace, multi-root session folder, or any path the runtime treats as its workspace, not the whole machine). | `cd <workspace-root>` then `apply` (no `-g`). |
| 2 | **User code directory** | A git repo, monorepo, or project the user is editing; no separate tool workspace, or workspace equals the repo root. | `cd <project-root>` then `apply` (no `-g`). |
| 3 | **Global home** | User explicitly wants machine-wide / user-wide agent defaults, or no workspace and no project path applies. **Last resort.** | `apply -g` (writes under `~/.claude`, `~/.gemini`, etc.). |

### Decision rules

1. **Prefer workspace over project root** when they differ. Example: OpenClaw keeps config under its workspace directory — do not assume the git repo root is the workspace. For Claude Code in a repo, workspace is usually the **project root** (tier 2); tier 1 and 2 collapse to the same path.
2. **Do not use `-g` for “this project / this workspace / this repo”.** Phrases like “在这个项目里”“这个 workspace”“切到 architect 写代码” → tier 1 or 2, always `cd` to that directory and `apply` without `-g`.
3. **Use `-g` only for tier 3**: “全局默认人格”“所有项目都用这个”“装到我的 Claude 用户目录（整机）” — and only after confirming there is no workspace or project scope.
4. **Never treat `~/.claude` or `~/.openclaw` as a substitute for a workspace** when the user scoped work to a workspace or repo. Global homes are not per-workspace.
5. If workspace path vs project root is unclear, ask one concise question (e.g. “OpenClaw workspace 路径还是 git 仓库根目录？”).

### Examples by tool

| Tool | Typical tier | Install root |
| --- | --- | --- |
| Claude Code (repo) | 2 (often same as 1) | Repository root → `CLAUDE.md` |
| Cursor / Copilot / Codex (repo) | 2 | Repository root |
| OpenClaw | 1 | Tool workspace directory (verify with user or existing layout) |
| Machine-wide Claude/Gemini defaults | 3 | `apply -g --ai claude` |

## Unified Workflow: `apply`

The `apply` command writes `.dprofile/generated/<adapter>/...` for every requested adapter, then activates verified adapters onto native paths under the **install root** (see Activation Policy).

1. Resolve install tier (table above) and `cd` to that directory for tier 1–2.
2. Validate the profile.
3. Select adapters via `--ai`.
4. Run `apply` without `-g` for tier 1–2; add `-g` only for tier 3.

```bash
# Tier 1 or 2: workspace or project root (most common)
cd /path/to/workspace-or-repo
python scripts/dprofile.py apply coding --ai claude,cursor

# Tier 3: global home only when intended
python scripts/dprofile.py apply linux-expert --ai claude -g
```

When `dprofile` is on `PATH`, the same commands use the `dprofile` executable.

Throughout this skill, **subcommands and flags are identical**; only the prefix differs: `python scripts/dprofile.py` from the dprofile checkout, or `dprofile` when installed. If the checkout lives elsewhere, use an absolute path to `scripts/dprofile.py`.

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

If multiple adapters share one native activation path (e.g. both `codex` and `opencode` write `AGENTS.md`), **the first adapter listed in `--ai` wins** for that path: the file receives that adapter's rendered content. Later adapters keep their `.dprofile/generated/` output but do not overwrite the shared path again. The runner prints this outcome; `skipped_duplicate_activation` in state lists `skipped`, `path`, and `active` (winner).

All generated or activated files should include a short managed marker when the target format allows comments:

```text
<!-- dprofile-managed: true; profile=<name>; adapter=<adapter> -->
```

If the format does not support comments, record ownership in `.dprofile/state.json`.

## CLI and bundled script

The bundled entry point performs deterministic file operations and exposes `--help`, `apply --help`, and `guide`.

**Prefer the script when the CLI is not installed.** From the cloned repository root (or pass an absolute path to `scripts/dprofile.py` if the skill checkout is nested):

```bash
python scripts/dprofile.py --help
python scripts/dprofile.py apply coding --ai claude,cursor
```

Default profile library resolves to bundled `dprofile/profiles/` for that checkout; use `--profiles-dir <path>` if the Agent uses a relocated library.

Use the same runner only after resolving the install tier.

**Tier 1–2** (run from workspace or project root):

```bash
cd /path/to/workspace-or-repo
python scripts/dprofile.py list
python scripts/dprofile.py validate-profile architect
python scripts/dprofile.py apply architect --ai claude,cursor,copilot
python scripts/dprofile.py apply architect --ai all --force
```

`list` reads `.dprofile/state.json` in the **current directory** only (`python scripts/dprofile.py list --help`).

**Tier 3** (global home, last resort):

```bash
python scripts/dprofile.py apply architect --ai claude -g
python scripts/dprofile.py show -g --ai claude
```

**Any tier** — profile library operations (from dprofile checkout or with `--profiles-dir`):

```bash
python scripts/dprofile.py diff architect writer
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

- Resolve install tier before `apply`; default to workspace or project root, not `-g`.
- Use `-g` only for tier 3 (global home). Never use `-g` when the user meant a workspace or repo.
- Do not guess workspace paths for unverified adapters; use `.dprofile/generated/` and ask or follow existing project conventions.
- Existing unmanaged activated files are skipped unless `--force` (after backup for managed overwrites).
- Back up existing target files before replacing managed or forced overwrites.
- Refuse to replace directories named `USER.md`, `SOUL.md`, `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`.
- Never remove or rewrite unrelated files.
- If a requested profile or adapter is invalid, stop and report the validation error.
