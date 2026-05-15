---
name: dprofile
description: Use this skill whenever the user wants an Agent to switch, list, inspect, compare, validate, or manage predefined Agent profiles/personas/workspaces across coding agents and IDEs. This includes requests like "switch to architect", "use ops profile", "切到写作人格", "dprofile switch", or anything involving USER.md, SOUL.md, AGENTS.md, SKILL.md, or IDE-specific agent instruction files. The Agent must classify the target as either an Agent-owned configuration directory or a code project before changing files.
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

1. If the user explicitly provides a target directory and target type, use it.
2. If the user asks to switch "this Agent", "my Agent", or a named Agent's own profile, treat the target as an Agent config target.
3. If the user says "this repo", "this project", "workspace", or points at source code, treat the target as a code project target.
4. If a system-level Agent directory is involved, require the user to provide or confirm the exact path.
5. If the target type is ambiguous, ask one concise clarifying question before changing files.

## Agent Config Workflow

For an Agent config target, follow that Agent's native configuration convention.

If the target Agent natively uses dprofile's three-layer model, write:

```text
target-agent-config/
  USER.md
  SOUL.md
  AGENTS.md
  .dprofile-state.json
  .dprofile-backups/
```

If the target Agent has a different native file, generate that file instead. Examples:

- Claude Code: `CLAUDE.md`
- Gemini CLI: `GEMINI.md`
- Codex and AGENTS.md-compatible agents: `AGENTS.md`

Workflow:

1. Validate that the selected profile exists and contains `USER.md`, `SOUL.md`, `AGENTS.md`, and `manifest.yaml`.
2. Validate that the target can safely receive the Agent-native files.
3. Back up existing managed target files before replacing them.
4. Write only files that belong to that Agent's configuration convention.
5. Write state metadata next to the Agent config or in the Agent's state directory.
6. Report the active profile, target directory, Agent type, changed files, and backup path.
7. Do not modify unrelated files.

## Code Project Workflow

For a code project target, do not write `USER.md`, `SOUL.md`, or `AGENTS.md` directly into the repository root by default.

Code projects may be used by many tools, including:

```text
agent
augment
claude
codebuddy
codex
continue
copilot
cursor
droid
gemini
hermes
kilocode
kiro
openclaw
opencode
qoder
roocode
trae
warp
windsurf
```

For project targets, dprofile acts as a profile compiler:

1. Validate the profile.
2. Create or update only the dprofile management area by default.
3. Generate adapter outputs under `.dprofile/generated/<adapter>/`.
4. Activate adapter outputs into real IDE or Agent paths only when the user explicitly asks for activation, or when using the install-style `init --ai` command.
5. Never overwrite a non-managed project file without backup and explicit confirmation.

Default project layout:

```text
project/
  .dprofile/
    state.json
    backups/
    generated/
      claude/
      codex/
      copilot/
      cursor/
      gemini/
      opencode/
      unknown-agent/
```

Activation may create native files such as:

```text
project/
  CLAUDE.md
  GEMINI.md
  AGENTS.md
  .cursor/
    rules/
      dprofile.mdc
  .github/
    copilot-instructions.md
```

Only create these activated files when the adapter path is verified and the user requested activation.

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

Project activation is opt-in for `apply` and default-on for `init --ai`.

Without activation:

- Write `.dprofile/state.json`.
- Write `.dprofile/generated/<adapter>/...`.
- Do not write root-level `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, or any IDE directory.

With activation or `init --ai`:

- Activate only requested adapters.
- Prefer tool-specific directories over root-level files when the tool supports them.
- For root-level files, explain the pollution tradeoff and activate only when the user requested that adapter.
- Preserve existing human-authored files unless the user explicitly approves merging or replacement.
- If multiple adapters share one activated path, activate that path once and still generate each adapter's `.dprofile/generated/` output.

All generated or activated files should include a short managed marker when the target format allows comments:

```text
<!-- dprofile-managed: true; profile=<name>; adapter=<adapter> -->
```

If the format does not support comments, record ownership in `.dprofile/state.json`.

## CLI

The bundled CLI performs deterministic file operations. It is intended for professional users and automation. It also exposes concise fallback guidance through `dprofile --help`, `dprofile init --help`, `dprofile apply --help`, and `dprofile guide`.

The Agent remains responsible for target classification, adapter selection, and safety checks. Prefer this `SKILL.md` for Agent behavior, then use the CLI to execute the chosen operation.

Use CLI commands only after deciding whether the target is an Agent config target or a code project target.

For Agent config targets:

```bash
dprofile list
dprofile validate-profile architect
dprofile switch architect --target-dir /path/to/agent-config
dprofile switch architect --target-dir /path/to/agent-config --mode copy
dprofile show --target-dir /path/to/agent-config
dprofile diff architect writer
```

For code project targets:

```bash
dprofile init architect --target-dir /path/to/project --ai codex
dprofile init architect --target-dir /path/to/project --ai claude,cursor,copilot
dprofile init architect --target-dir /path/to/project --ai all
dprofile init architect --target-dir /path/to/project --ai all --force
```

`init --ai` is the install-style workflow. It always writes `.dprofile/generated/<adapter>/` and activates verified adapters into their native project paths.

Use `apply` when you want to generate without activation first:

```bash
dprofile apply architect --target-dir /path/to/project --agents all
dprofile apply architect --target-dir /path/to/project --agents claude,cursor --activate
```

Use `--profiles-dir /path/to/profiles` when the profile library is not this skill's bundled `profiles/` directory.

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

- Never guess a system-level Agent directory.
- Never use `switch` on a code project root unless the user explicitly wants raw three-file output there.
- Prefer `.dprofile/generated/` for code projects until activation is requested.
- Back up existing target files before switching, activating, merging, or replacing.
- Refuse to replace directories named `USER.md`, `SOUL.md`, `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md`.
- Never remove or rewrite unrelated files.
- If a requested profile, target directory, or adapter is invalid, stop and report the validation error.
