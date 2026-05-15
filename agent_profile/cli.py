#!/usr/bin/env python3
"""Manage USER.md/SOUL.md/AGENTS.md agent profile sets."""

from __future__ import annotations

import argparse
import difflib
import json
import os
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent


REQUIRED_FILES = ("USER.md", "SOUL.md", "AGENTS.md", "manifest.yaml")
PROFILE_FILES = ("USER.md", "SOUL.md", "AGENTS.md")
STATE_FILE = ".agent-profile-state.json"
BACKUP_DIR = ".agent-profile-backups"
PROJECT_DIR = ".dprofile"
PROJECT_STATE_FILE = "state.json"
PROJECT_BACKUP_DIR = "backups"
PROJECT_GENERATED_DIR = "generated"
MANAGED_MARKER_PREFIX = "<!-- dprofile-managed: true;"
ALL_ADAPTERS = (
    "agent",
    "augment",
    "claude",
    "codebuddy",
    "codex",
    "continue",
    "copilot",
    "cursor",
    "droid",
    "gemini",
    "hermes",
    "kilocode",
    "kiro",
    "openclaw",
    "opencode",
    "qoder",
    "roocode",
    "trae",
    "warp",
    "windsurf",
)


@dataclass(frozen=True)
class Profile:
    name: str
    path: Path
    description: str
    tags: tuple[str, ...]


@dataclass(frozen=True)
class Adapter:
    name: str
    generated_path: Path
    activated_path: Path | None
    verified: bool
    format: str
    layers: tuple[str, ...]


class ProfileError(RuntimeError):
    pass


TOP_LEVEL_EPILOG = """\
Primary workflow lives in SKILL.md:
  SKILL.md is the authority for Agent judgment, target classification, adapter
  safety, and project-vs-Agent-directory decisions. The CLI is the deterministic
  executor and fallback guide.

Agent config targets:
  Use switch for Agent-owned config directories. This writes the raw dprofile
  three-layer source files: USER.md, SOUL.md, and AGENTS.md.

Code project targets:
  Use init for code projects. It installs adapter-native files for AI tools and
  keeps dprofile state under .dprofile/.

  Use apply when you want to generate adapter outputs first without activating
  native files.

Examples:
  dprofile switch coding --target-dir ~/.codex
  dprofile init coding --target-dir . --ai codex
  dprofile init coding --target-dir . --ai claude,cursor,copilot
  dprofile apply coding --target-dir . --agents all

Run `dprofile guide` for the full usage protocol.
"""


PROJECT_HELP_EPILOG = """\
Adapter compatibility:
  Claude/Gemini receive full profile context: USER.md, SOUL.md, and AGENTS.md.
  Cursor/Copilot/Codex/OpenCode receive operating protocol focused output.
  Unverified adapters generate only .dprofile/generated/<adapter>/INSTRUCTIONS.md.

Verified project adapters:
  claude   -> CLAUDE.md
  cursor   -> .cursor/rules/dprofile.mdc
  copilot  -> .github/copilot-instructions.md
  codex    -> AGENTS.md
  gemini   -> GEMINI.md
  opencode -> AGENTS.md
"""


VERIFIED_ADAPTERS: dict[str, Adapter] = {
    "claude": Adapter("claude", Path("claude/CLAUDE.md"), Path("CLAUDE.md"), True, "markdown-full", ("user", "soul", "agents")),
    "cursor": Adapter("cursor", Path("cursor/dprofile.mdc"), Path(".cursor/rules/dprofile.mdc"), True, "cursor-mdc", ("agents",)),
    "copilot": Adapter(
        "copilot",
        Path("copilot/copilot-instructions.md"),
        Path(".github/copilot-instructions.md"),
        True,
        "copilot",
        ("agents",),
    ),
    "codex": Adapter("codex", Path("codex/AGENTS.md"), Path("AGENTS.md"), True, "agents-md", ("agents",)),
    "gemini": Adapter("gemini", Path("gemini/GEMINI.md"), Path("GEMINI.md"), True, "markdown-full", ("user", "soul", "agents")),
    "opencode": Adapter("opencode", Path("opencode/AGENTS.md"), Path("AGENTS.md"), True, "agents-md", ("agents",)),
}


def package_root() -> Path:
    return Path(__file__).resolve().parent


def default_profiles_dir() -> Path:
    env_dir = os.environ.get("AGENT_PROFILE_PROFILES_DIR")
    if env_dir:
        return Path(env_dir).expanduser().resolve()
    return package_root() / "profiles"


def resolve_profiles_dir(raw_profiles_dir: str | None) -> Path:
    if raw_profiles_dir:
        return Path(raw_profiles_dir).expanduser().resolve()
    return default_profiles_dir()


def resolve_target_dir(raw_target_dir: str | None) -> Path:
    if not raw_target_dir:
        raise ProfileError("--target-dir is required for this command")
    return Path(raw_target_dir).expanduser().resolve()


def project_state_path(target_dir: Path) -> Path:
    return target_dir / PROJECT_DIR / PROJECT_STATE_FILE


def adapter_for(name: str) -> Adapter:
    if name in VERIFIED_ADAPTERS:
        return VERIFIED_ADAPTERS[name]
    if name in ALL_ADAPTERS:
        return Adapter(name, Path(name) / "INSTRUCTIONS.md", None, False, "manual", ("user", "soul", "agents"))
    raise ProfileError(f"unknown adapter: {name}")


def parse_adapters(raw_agents: str) -> list[str]:
    names = [item.strip().lower() for item in raw_agents.split(",") if item.strip()]
    if not names:
        raise ProfileError("--agents must name at least one adapter")
    if "all" in names:
        return list(ALL_ADAPTERS)
    seen: set[str] = set()
    ordered: list[str] = []
    for name in names:
        adapter_for(name)
        if name not in seen:
            ordered.append(name)
            seen.add(name)
    return ordered


def read_manifest_value(manifest: Path, key: str) -> str:
    prefix = f"{key}:"
    for line in manifest.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            return stripped[len(prefix) :].strip().strip('"').strip("'")
    return ""


def read_manifest_tags(manifest: Path) -> tuple[str, ...]:
    tags: list[str] = []
    in_tags = False
    for line in manifest.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped == "tags:":
            in_tags = True
            continue
        if in_tags and stripped.startswith("- "):
            tags.append(stripped[2:].strip())
            continue
        if in_tags and stripped and not stripped.startswith("- "):
            break
    return tuple(tags)


def read_profile_text(profile: Profile, filename: str) -> str:
    return (profile.path / filename).read_text(encoding="utf-8").strip()


def render_marker(profile: Profile, adapter: Adapter) -> str:
    return f"<!-- dprofile-managed: true; profile={profile.name}; adapter={adapter.name} -->"


def render_profile_summary(profile: Profile) -> list[str]:
    description = profile.description or "No description."
    tags = ", ".join(profile.tags) if profile.tags else "none"
    return [
        "## Profile",
        "",
        f"- Name: {profile.name}",
        f"- Description: {description}",
        f"- Tags: {tags}",
        "",
    ]


def render_layers(profile: Profile, layers: tuple[str, ...]) -> list[str]:
    sections: list[str] = []
    if "user" in layers:
        sections.extend(["## User Context", "", read_profile_text(profile, "USER.md"), ""])
    if "soul" in layers:
        sections.extend(["## Agent Identity", "", read_profile_text(profile, "SOUL.md"), ""])
    if "agents" in layers:
        sections.extend(["## Operating Protocol", "", read_profile_text(profile, "AGENTS.md"), ""])
    return sections


def render_adapter_file(profile: Profile, adapter: Adapter) -> str:
    marker = render_marker(profile, adapter)
    if adapter.format == "cursor-mdc":
        lines = [
            "---",
            f"description: dprofile {profile.name} operating protocol",
            "globs: **/*",
            "alwaysApply: true",
            "---",
            marker,
            f"# Cursor Rules for {profile.name}",
            "",
        ]
        lines.extend(render_layers(profile, adapter.layers))
        return "\n".join(lines)

    if adapter.format == "copilot":
        lines = [
            marker,
            "# GitHub Copilot Instructions",
            "",
            f"Active dprofile: {profile.name}",
            "",
        ]
        lines.extend(render_layers(profile, adapter.layers))
        return "\n".join(lines)

    if adapter.format == "agents-md":
        lines = [
            marker,
            "# AGENTS.md",
            "",
            f"Active dprofile: {profile.name}",
            "",
            "This file is generated for AGENTS.md-compatible coding agents.",
            "",
        ]
        lines.extend(render_layers(profile, adapter.layers))
        return "\n".join(lines)

    if adapter.format == "manual":
        lines = [
            marker,
            f"# dprofile {profile.name} for {adapter.name}",
            "",
            "Manual activation required.",
            "",
        ]
        lines.extend(render_profile_summary(profile))
        lines.extend(render_layers(profile, adapter.layers))
        lines.extend(["## Adapter Notes", "", f"No verified native path is known for `{adapter.name}`.", ""])
        return "\n".join(lines)

    lines = [
        marker,
        f"# dprofile {profile.name} for {adapter.name}",
        "",
    ]
    lines.extend(render_profile_summary(profile))
    lines.extend(render_layers(profile, adapter.layers))
    lines.extend(["## Adapter Notes", "", f"This file was generated for the `{adapter.name}` adapter.", ""])
    return "\n".join(lines)


def load_profile(profile_root: Path, name: str) -> Profile:
    path = profile_root / name
    manifest = path / "manifest.yaml"
    description = read_manifest_value(manifest, "description") if manifest.exists() else ""
    tags = read_manifest_tags(manifest) if manifest.exists() else ()
    return Profile(name=name, path=path, description=description, tags=tags)


def discover_profiles(profile_root: Path) -> list[Profile]:
    if not profile_root.exists():
        return []
    profiles = []
    for item in sorted(profile_root.iterdir(), key=lambda p: p.name):
        if item.is_dir():
            profiles.append(load_profile(profile_root, item.name))
    return profiles


def validate_profile(profile_root: Path, name: str) -> list[str]:
    profile = load_profile(profile_root, name)
    errors: list[str] = []
    if not profile.path.exists():
        return [f"profile not found: {name}"]
    if not profile.path.is_dir():
        return [f"profile path is not a directory: {profile.path}"]
    for filename in REQUIRED_FILES:
        path = profile.path / filename
        if not path.exists():
            errors.append(f"missing {filename}")
        elif not path.is_file():
            errors.append(f"{filename} is not a file")
        elif filename != "manifest.yaml" and not path.read_text(encoding="utf-8").strip():
            errors.append(f"{filename} is empty")
    manifest = profile.path / "manifest.yaml"
    if manifest.exists():
        manifest_name = read_manifest_value(manifest, "name")
        if manifest_name and manifest_name != name:
            errors.append(f"manifest name {manifest_name!r} does not match directory {name!r}")
    return errors


def state_path(target_dir: Path) -> Path:
    return target_dir / STATE_FILE


def read_state(target_dir: Path) -> dict[str, object] | None:
    path = state_path(target_dir)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ProfileError(f"invalid state file {path}: {exc}") from exc


def validate_target(target_dir: Path) -> list[str]:
    errors: list[str] = []
    if not target_dir.exists():
        errors.append(f"target directory does not exist: {target_dir}")
        return errors
    if not target_dir.is_dir():
        errors.append(f"target path is not a directory: {target_dir}")
        return errors
    for filename in PROFILE_FILES:
        path = target_dir / filename
        if path.exists() and path.is_dir() and not path.is_symlink():
            errors.append(f"refusing to replace directory: {path}")
    if state_path(target_dir).exists():
        read_state(target_dir)
    return errors


def validate_project_target(target_dir: Path) -> list[str]:
    errors: list[str] = []
    if not target_dir.exists():
        errors.append(f"target directory does not exist: {target_dir}")
        return errors
    if not target_dir.is_dir():
        errors.append(f"target path is not a directory: {target_dir}")
        return errors
    dprofile_dir = target_dir / PROJECT_DIR
    if dprofile_dir.exists() and not dprofile_dir.is_dir():
        errors.append(f"refusing to replace file: {dprofile_dir}")
    return errors


def backup_target(target_dir: Path) -> Path | None:
    existing = [target_dir / filename for filename in PROFILE_FILES if (target_dir / filename).exists()]
    state = state_path(target_dir)
    if state.exists():
        existing.append(state)
    if not existing:
        return None

    backup = target_dir / BACKUP_DIR / datetime.now().strftime("%Y%m%d-%H%M%S")
    backup.mkdir(parents=True, exist_ok=False)
    for source in existing:
        target = backup / source.name
        if source.is_symlink():
            resolved = source.resolve()
            if resolved.exists():
                shutil.copy2(resolved, target)
            else:
                target.write_text(f"broken symlink: {os.readlink(source)}\n", encoding="utf-8")
        else:
            shutil.copy2(source, target)
    return backup


def replace_target_file(source: Path, target: Path, mode: str) -> None:
    if target.exists() or target.is_symlink():
        if target.is_dir() and not target.is_symlink():
            raise ProfileError(f"refusing to replace directory: {target}")
        target.unlink()
    if mode == "copy":
        shutil.copy2(source, target)
        return
    relative_source = os.path.relpath(source, start=target.parent)
    target.symlink_to(relative_source)


def relative_to_target(target_dir: Path, path: Path) -> str:
    return path.relative_to(target_dir).as_posix()


def is_managed_file(path: Path) -> bool:
    if not path.exists() or not path.is_file():
        return False
    first_line = path.read_text(encoding="utf-8").splitlines()[:1]
    return bool(first_line and first_line[0].startswith(MANAGED_MARKER_PREFIX))


def backup_project_file(target_dir: Path, path: Path) -> Path:
    relative = path.relative_to(target_dir)
    backup = target_dir / PROJECT_DIR / PROJECT_BACKUP_DIR / datetime.now().strftime("%Y%m%d-%H%M%S") / relative
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup)
    return backup


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_activated_file(target_dir: Path, path: Path, content: str, force: bool) -> Path | None:
    backup = None
    if path.exists():
        if path.is_dir() and not path.is_symlink():
            raise ProfileError(f"refusing to replace directory: {path}")
        if not force and not is_managed_file(path):
            raise ProfileError(f"refusing to overwrite unmanaged file: {path}")
        backup = backup_project_file(target_dir, path)
    write_text(path, content)
    return backup


def write_project_state(
    target_dir: Path,
    profile: Profile,
    profiles_dir: Path,
    adapters: list[str],
    generated: list[Path],
    activated: list[Path],
    skipped_activation: list[str],
    backups: list[Path],
) -> None:
    state = {
        "scope": "project",
        "active_profile": profile.name,
        "source_profile_path": str(profile.path),
        "profiles_dir": str(profiles_dir),
        "target_dir": str(target_dir),
        "applied_at": datetime.now(timezone.utc).isoformat(),
        "adapters": adapters,
        "generated_files": [relative_to_target(target_dir, path) for path in generated],
        "activated_files": [relative_to_target(target_dir, path) for path in activated],
        "skipped_activation": skipped_activation,
        "backup_paths": [relative_to_target(target_dir, path) for path in backups],
    }
    path = project_state_path(target_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def apply_project_profile(
    profiles_dir: Path,
    target_dir: Path,
    name: str,
    adapters: list[str],
    activate: bool,
    force: bool,
) -> tuple[list[Path], list[Path], list[str], list[Path]]:
    errors = validate_profile(profiles_dir, name)
    if errors:
        raise ProfileError("; ".join(errors))
    target_errors = validate_project_target(target_dir)
    if target_errors:
        raise ProfileError("; ".join(target_errors))

    profile = load_profile(profiles_dir, name)
    generated: list[Path] = []
    activated: list[Path] = []
    skipped_activation: list[str] = []
    backups: list[Path] = []

    for adapter_name in adapters:
        adapter = adapter_for(adapter_name)
        content = render_adapter_file(profile, adapter)
        generated_path = target_dir / PROJECT_DIR / PROJECT_GENERATED_DIR / adapter.generated_path
        write_text(generated_path, content)
        generated.append(generated_path)

        if not activate:
            continue
        if not adapter.verified or adapter.activated_path is None:
            skipped_activation.append(adapter.name)
            continue
        activated_path = target_dir / adapter.activated_path
        if activated_path in activated:
            continue
        backup = write_activated_file(target_dir, activated_path, content, force)
        if backup:
            backups.append(backup)
        activated.append(activated_path)

    write_project_state(target_dir, profile, profiles_dir, adapters, generated, activated, skipped_activation, backups)
    return generated, activated, skipped_activation, backups


def write_state(
    target_dir: Path,
    profile: Profile,
    profiles_dir: Path,
    mode: str,
    backup: Path | None,
    changed: list[Path],
) -> None:
    state = {
        "active_profile": profile.name,
        "source_profile_path": str(profile.path),
        "profiles_dir": str(profiles_dir),
        "target_dir": str(target_dir),
        "switched_at": datetime.now(timezone.utc).isoformat(),
        "backup_path": str(backup) if backup else None,
        "write_mode": mode,
        "files": [str(path) for path in changed],
    }
    state_path(target_dir).write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def switch_profile(profiles_dir: Path, target_dir: Path, name: str, mode: str) -> tuple[Path | None, list[Path]]:
    errors = validate_profile(profiles_dir, name)
    if errors:
        raise ProfileError("; ".join(errors))
    target_errors = validate_target(target_dir)
    if target_errors:
        raise ProfileError("; ".join(target_errors))

    target_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_target(target_dir)
    profile = load_profile(profiles_dir, name)

    changed: list[Path] = []
    for filename in PROFILE_FILES:
        target = target_dir / filename
        replace_target_file(profile.path / filename, target, mode)
        changed.append(target)

    write_state(target_dir, profile, profiles_dir, mode, backup, changed)
    return backup, changed


def read_file(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines(keepends=True)


def command_list(args: argparse.Namespace) -> int:
    profiles_dir = resolve_profiles_dir(args.profiles_dir)
    profiles = discover_profiles(profiles_dir)
    active = None
    if args.target_dir:
        target_dir = resolve_target_dir(args.target_dir)
        state = read_state(target_dir)
        active = state.get("active_profile") if state else None

    if not profiles:
        print("No profiles found.")
        return 0
    for profile in profiles:
        marker = "*" if profile.name == active else " "
        tags = f" [{', '.join(profile.tags)}]" if profile.tags else ""
        description = f" - {profile.description}" if profile.description else ""
        print(f"{marker} {profile.name}{description}{tags}")
    return 0


def command_validate_profile(args: argparse.Namespace) -> int:
    profiles_dir = resolve_profiles_dir(args.profiles_dir)
    names = [args.profile] if args.profile else [profile.name for profile in discover_profiles(profiles_dir)]
    if not names:
        print("No profiles found.")
        return 1

    failed = False
    for name in names:
        errors = validate_profile(profiles_dir, name)
        if errors:
            failed = True
            print(f"{name}: invalid")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"{name}: ok")
    return 1 if failed else 0


def command_validate_target(args: argparse.Namespace) -> int:
    try:
        target_dir = resolve_target_dir(args.target_dir)
        errors = validate_target(target_dir)
    except ProfileError as exc:
        print(f"target: invalid")
        print(f"  - {exc}")
        return 1
    if errors:
        print("target: invalid")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"target: ok ({target_dir})")
    return 0


def command_switch(args: argparse.Namespace) -> int:
    profiles_dir = resolve_profiles_dir(args.profiles_dir)
    try:
        target_dir = resolve_target_dir(args.target_dir)
        backup, changed = switch_profile(profiles_dir, target_dir, args.profile, args.mode)
    except ProfileError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Active profile: {args.profile}")
    print(f"Target directory: {target_dir}")
    print(f"Write mode: {args.mode}")
    print(f"Backup: {backup if backup else 'none'}")
    print("Changed files:")
    for path in changed:
        if path.is_symlink():
            print(f"  - {path} -> {os.readlink(path)}")
        else:
            print(f"  - {path}")
    print(f"State: {state_path(target_dir)}")
    return 0


def command_apply(args: argparse.Namespace) -> int:
    profiles_dir = resolve_profiles_dir(args.profiles_dir)
    try:
        target_dir = resolve_target_dir(args.target_dir)
        adapters = parse_adapters(args.agents)
        generated, activated, skipped_activation, backups = apply_project_profile(
            profiles_dir,
            target_dir,
            args.profile,
            adapters,
            args.activate,
            args.force,
        )
    except ProfileError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Applied profile: {args.profile}")
    print(f"Target directory: {target_dir}")
    print(f"Adapters: {', '.join(adapters)}")
    print(f"Activation: {'enabled' if args.activate else 'disabled'}")
    print("Generated files:")
    for path in generated:
        print(f"  - {relative_to_target(target_dir, path)}")
    if activated:
        print("Activated files:")
        for path in activated:
            print(f"  - {relative_to_target(target_dir, path)}")
    if skipped_activation:
        print(f"Skipped activation for unverified adapters: {', '.join(skipped_activation)}")
    if backups:
        print("Backups:")
        for path in backups:
            print(f"  - {relative_to_target(target_dir, path)}")
    print(f"State: {relative_to_target(target_dir, project_state_path(target_dir))}")
    return 0


def command_init(args: argparse.Namespace) -> int:
    profiles_dir = resolve_profiles_dir(args.profiles_dir)
    try:
        target_dir = resolve_target_dir(args.target_dir)
        adapters = parse_adapters(args.ai)
        generated, activated, skipped_activation, backups = apply_project_profile(
            profiles_dir,
            target_dir,
            args.profile,
            adapters,
            True,
            args.force,
        )
    except ProfileError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Initialized profile: {args.profile}")
    print(f"Target directory: {target_dir}")
    print(f"AI adapters: {', '.join(adapters)}")
    print("Generated files:")
    for path in generated:
        print(f"  - {relative_to_target(target_dir, path)}")
    if activated:
        print("Activated files:")
        for path in activated:
            print(f"  - {relative_to_target(target_dir, path)}")
    if skipped_activation:
        print(f"Skipped activation for unverified adapters: {', '.join(skipped_activation)}")
    if backups:
        print("Backups:")
        for path in backups:
            print(f"  - {relative_to_target(target_dir, path)}")
    print(f"State: {relative_to_target(target_dir, project_state_path(target_dir))}")
    return 0


def command_guide(args: argparse.Namespace) -> int:
    print(
        dedent(
            """\
            dprofile usage guide

            SKILL.md is the primary Agent workflow.
            The CLI is the secondary deterministic executor and fallback help
            surface for humans or Agents that do not have the skill installed.

            Use switch for Agent-owned config directories:
              dprofile switch coding --target-dir ~/.codex

            switch writes the raw dprofile source files:
              USER.md
              SOUL.md
              AGENTS.md

            Use init for code projects:
              dprofile init coding --target-dir . --ai codex
              dprofile init coding --target-dir . --ai claude,cursor,copilot
              dprofile init coding --target-dir . --ai all

            init writes .dprofile/generated/<adapter>/ and activates verified
            adapter-native files such as AGENTS.md, CLAUDE.md, GEMINI.md,
            .cursor/rules/dprofile.mdc, and .github/copilot-instructions.md.

            Use apply for review-first project generation:
              dprofile apply coding --target-dir . --agents all
              dprofile apply coding --target-dir . --agents codex --activate

            Adapter layer policy:
              claude, gemini: USER.md + SOUL.md + AGENTS.md
              cursor, copilot: AGENTS.md only
              codex, opencode: profile summary + AGENTS.md
              unverified adapters: generated-only manual instructions

            Safety:
              Project mode keeps state and generated files under .dprofile/.
              Existing unmanaged activated files are not overwritten unless
              --force is passed.
            """
        )
    )
    return 0


def command_show(args: argparse.Namespace) -> int:
    profiles_dir = resolve_profiles_dir(args.profiles_dir)
    if args.profile:
        errors = validate_profile(profiles_dir, args.profile)
        if errors:
            print(f"{args.profile}: invalid")
            for error in errors:
                print(f"  - {error}")
            return 1
        profile = load_profile(profiles_dir, args.profile)
        print(f"Profile: {profile.name}")
        print(f"Description: {profile.description}")
        print(f"Path: {profile.path}")
        return 0

    try:
        target_dir = resolve_target_dir(args.target_dir)
        state = read_state(target_dir)
    except ProfileError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    if not state:
        print("No active profile state.")
        return 1

    print(f"Active profile: {state.get('active_profile')}")
    print(f"Target directory: {target_dir}")
    print(f"Write mode: {state.get('write_mode')}")
    print(f"Source profile: {state.get('source_profile_path')}")
    print(f"Backup: {state.get('backup_path')}")
    for filename in PROFILE_FILES:
        path = target_dir / filename
        if path.is_symlink():
            print(f"{filename}: {os.readlink(path)}")
        elif path.exists():
            print(f"{filename}: regular file")
        else:
            print(f"{filename}: missing")
    return 0


def command_diff(args: argparse.Namespace) -> int:
    profiles_dir = resolve_profiles_dir(args.profiles_dir)
    for name in (args.left, args.right):
        errors = validate_profile(profiles_dir, name)
        if errors:
            print(f"{name}: invalid - {'; '.join(errors)}", file=sys.stderr)
            return 1

    left_base = profiles_dir / args.left
    right_base = profiles_dir / args.right
    emitted = False
    for filename in PROFILE_FILES:
        left_file = left_base / filename
        right_file = right_base / filename
        diff = difflib.unified_diff(
            read_file(left_file),
            read_file(right_file),
            fromfile=f"{args.left}/{filename}",
            tofile=f"{args.right}/{filename}",
        )
        lines = list(diff)
        if lines:
            emitted = True
            print("".join(lines), end="")
    if not emitted:
        print("No differences.")
    return 0


def add_common_profile_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--profiles-dir", help="profile library directory; defaults to this skill's profiles/")


def build_parser() -> argparse.ArgumentParser:
    formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(
        prog="agent-profile",
        description="Manage dprofile persona sets for Agent configs and code project AI adapters.",
        epilog=TOP_LEVEL_EPILOG,
        formatter_class=formatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    guide_parser = subparsers.add_parser(
        "guide",
        help="explain when to use switch, init, and apply",
        formatter_class=formatter,
    )
    guide_parser.set_defaults(func=command_guide)

    list_parser = subparsers.add_parser("list", help="list available profiles")
    add_common_profile_arg(list_parser)
    list_parser.add_argument("--target-dir", help="optional target directory used to mark the active profile")
    list_parser.set_defaults(func=command_list)

    switch_parser = subparsers.add_parser("switch", help="switch a target Agent config directory to a profile")
    add_common_profile_arg(switch_parser)
    switch_parser.add_argument("profile")
    switch_parser.add_argument("--target-dir", required=True, help="Agent configuration directory to update")
    switch_parser.add_argument("--mode", choices=("symlink", "copy"), default="symlink")
    switch_parser.set_defaults(func=command_switch)

    apply_parser = subparsers.add_parser(
        "apply",
        help="apply a profile to a code project through adapters",
        epilog=PROJECT_HELP_EPILOG,
        formatter_class=formatter,
    )
    add_common_profile_arg(apply_parser)
    apply_parser.add_argument("profile")
    apply_parser.add_argument("--target-dir", required=True, help="code project directory to update")
    apply_parser.add_argument("--agents", default="all", help="comma-separated adapter names, or all")
    apply_parser.add_argument("--activate", action="store_true", help="write verified adapter outputs to native paths")
    apply_parser.add_argument("--force", action="store_true", help="overwrite unmanaged activated files after backup")
    apply_parser.set_defaults(func=command_apply)

    init_parser = subparsers.add_parser(
        "init",
        help="install project adapter files for AI assistants",
        epilog=PROJECT_HELP_EPILOG,
        formatter_class=formatter,
    )
    add_common_profile_arg(init_parser)
    init_parser.add_argument("profile")
    init_parser.add_argument("--target-dir", required=True, help="code project directory to initialize")
    init_parser.add_argument("--ai", default="all", help="comma-separated AI adapter names, or all")
    init_parser.add_argument("--force", action="store_true", help="overwrite unmanaged activated files after backup")
    init_parser.set_defaults(func=command_init)

    show_parser = subparsers.add_parser("show", help="show target state or a named profile")
    add_common_profile_arg(show_parser)
    show_parser.add_argument("profile", nargs="?", help="profile to inspect; omit to show target state")
    show_parser.add_argument("--target-dir", help="Agent configuration directory to inspect")
    show_parser.set_defaults(func=command_show)

    diff_parser = subparsers.add_parser("diff", help="diff two profiles")
    add_common_profile_arg(diff_parser)
    diff_parser.add_argument("left")
    diff_parser.add_argument("right")
    diff_parser.set_defaults(func=command_diff)

    validate_profile_parser = subparsers.add_parser(
        "validate-profile", aliases=("validate",), help="validate one profile or all profiles"
    )
    add_common_profile_arg(validate_profile_parser)
    validate_profile_parser.add_argument("profile", nargs="?")
    validate_profile_parser.set_defaults(func=command_validate_profile)

    validate_target_parser = subparsers.add_parser("validate-target", help="validate a target Agent config directory")
    validate_target_parser.add_argument("--target-dir", required=True)
    validate_target_parser.set_defaults(func=command_validate_target)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
