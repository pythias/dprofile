from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI = REPO_ROOT / "scripts" / "agent_profile.py"


def write_profile(profiles_dir: Path, name: str, text: str) -> None:
    profile = profiles_dir / name
    profile.mkdir(parents=True)
    (profile / "manifest.yaml").write_text(
        "\n".join(
            [
                f"name: {name}",
                f"description: {name} profile",
                "files:",
                "  user: USER.md",
                "  soul: SOUL.md",
                "  agents: AGENTS.md",
                "tags:",
                "  - test",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (profile / "USER.md").write_text(f"# User\n\n{text}\n", encoding="utf-8")
    (profile / "SOUL.md").write_text(f"# Soul\n\n{text}\n", encoding="utf-8")
    (profile / "AGENTS.md").write_text(f"# Agents\n\n{text}\n", encoding="utf-8")


def run_cli(profiles_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args, "--profiles-dir", str(profiles_dir)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def run_raw_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class AgentProfileTests(unittest.TestCase):
    def test_switch_creates_symlinks_and_state_in_target_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles_dir = root / "profiles"
            target_dir = root / "agent-config"
            target_dir.mkdir()
            write_profile(profiles_dir, "architect", "architecture")

            result = run_cli(profiles_dir, "switch", "architect", "--target-dir", str(target_dir))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Active profile: architect", result.stdout)
            self.assertIn(f"Target directory: {target_dir.resolve()}", result.stdout)
            state = json.loads((target_dir / ".agent-profile-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["active_profile"], "architect")
            self.assertEqual(state["write_mode"], "symlink")
            for filename in ("USER.md", "SOUL.md", "AGENTS.md"):
                current_file = target_dir / filename
                self.assertTrue(current_file.is_symlink())
                self.assertEqual(current_file.resolve(), (profiles_dir / "architect" / filename).resolve())

    def test_switch_copy_mode_writes_regular_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles_dir = root / "profiles"
            target_dir = root / "agent-config"
            target_dir.mkdir()
            write_profile(profiles_dir, "architect", "architecture")

            result = run_cli(
                profiles_dir,
                "switch",
                "architect",
                "--target-dir",
                str(target_dir),
                "--mode",
                "copy",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((target_dir / "USER.md").is_symlink())
            self.assertIn("architecture", (target_dir / "USER.md").read_text(encoding="utf-8"))
            state = json.loads((target_dir / ".agent-profile-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["write_mode"], "copy")

    def test_switch_backs_up_previous_target_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles_dir = root / "profiles"
            target_dir = root / "agent-config"
            target_dir.mkdir()
            write_profile(profiles_dir, "architect", "architecture")
            write_profile(profiles_dir, "writer", "writing")
            self.assertEqual(
                run_cli(profiles_dir, "switch", "architect", "--target-dir", str(target_dir)).returncode,
                0,
            )

            result = run_cli(profiles_dir, "switch", "writer", "--target-dir", str(target_dir))

            self.assertEqual(result.returncode, 0, result.stderr)
            backups = list((target_dir / ".agent-profile-backups").iterdir())
            self.assertEqual(len(backups), 1)
            self.assertIn("architecture", (backups[0] / "USER.md").read_text(encoding="utf-8"))
            state = json.loads((target_dir / ".agent-profile-state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["active_profile"], "writer")

    def test_validate_profile_reports_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            profiles_dir = Path(temp) / "profiles"
            write_profile(profiles_dir, "broken", "broken")
            (profiles_dir / "broken" / "SOUL.md").unlink()

            result = run_cli(profiles_dir, "validate-profile", "broken")

            self.assertEqual(result.returncode, 1)
            self.assertIn("broken: invalid", result.stdout)
            self.assertIn("missing SOUL.md", result.stdout)

    def test_validate_target_rejects_directory_file_slot(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target_dir = Path(temp) / "agent-config"
            target_dir.mkdir()
            (target_dir / "USER.md").mkdir()

            result = subprocess.run(
                [sys.executable, str(CLI), "validate-target", "--target-dir", str(target_dir)],
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("target: invalid", result.stdout)
            self.assertIn("refusing to replace directory", result.stdout)

    def test_diff_outputs_unified_diff(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            profiles_dir = Path(temp) / "profiles"
            write_profile(profiles_dir, "architect", "architecture")
            write_profile(profiles_dir, "writer", "writing")

            result = run_cli(profiles_dir, "diff", "architect", "writer")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("--- architect/USER.md", result.stdout)
            self.assertIn("+++ writer/USER.md", result.stdout)
            self.assertIn("-architecture", result.stdout)
            self.assertIn("+writing", result.stdout)

    def test_list_marks_active_profile_when_target_dir_is_provided(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles_dir = root / "profiles"
            target_dir = root / "agent-config"
            target_dir.mkdir()
            write_profile(profiles_dir, "architect", "architecture")
            write_profile(profiles_dir, "writer", "writing")
            self.assertEqual(
                run_cli(profiles_dir, "switch", "writer", "--target-dir", str(target_dir)).returncode,
                0,
            )

            result = run_cli(profiles_dir, "list", "--target-dir", str(target_dir))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("* writer - writer profile", result.stdout)
            self.assertIn("  architect - architect profile", result.stdout)

    def test_apply_generates_project_adapter_outputs_without_activation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles_dir = root / "profiles"
            target_dir = root / "project"
            target_dir.mkdir()
            write_profile(profiles_dir, "coding", "implementation")

            result = run_cli(
                profiles_dir,
                "apply",
                "coding",
                "--target-dir",
                str(target_dir),
                "--agents",
                "claude,cursor,augment",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target_dir / ".dprofile/generated/claude/CLAUDE.md").is_file())
            self.assertTrue((target_dir / ".dprofile/generated/cursor/dprofile.mdc").is_file())
            self.assertTrue((target_dir / ".dprofile/generated/augment/INSTRUCTIONS.md").is_file())
            self.assertFalse((target_dir / "CLAUDE.md").exists())
            self.assertFalse((target_dir / ".cursor").exists())
            state = json.loads((target_dir / ".dprofile/state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["scope"], "project")
            self.assertEqual(state["active_profile"], "coding")
            self.assertEqual(state["activated_files"], [])

    def test_apply_activate_writes_verified_adapter_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles_dir = root / "profiles"
            target_dir = root / "project"
            target_dir.mkdir()
            write_profile(profiles_dir, "coding", "implementation")

            result = run_cli(
                profiles_dir,
                "apply",
                "coding",
                "--target-dir",
                str(target_dir),
                "--agents",
                "claude,cursor",
                "--activate",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Activated files:", result.stdout)
            self.assertIn("dprofile-managed: true", (target_dir / "CLAUDE.md").read_text(encoding="utf-8"))
            self.assertIn(
                "implementation",
                (target_dir / ".cursor/rules/dprofile.mdc").read_text(encoding="utf-8"),
            )
            state = json.loads((target_dir / ".dprofile/state.json").read_text(encoding="utf-8"))
            self.assertEqual(
                sorted(Path(path).as_posix() for path in state["activated_files"]),
                [".cursor/rules/dprofile.mdc", "CLAUDE.md"],
            )

    def test_apply_does_not_activate_unverified_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles_dir = root / "profiles"
            target_dir = root / "project"
            target_dir.mkdir()
            write_profile(profiles_dir, "coding", "implementation")

            result = run_cli(
                profiles_dir,
                "apply",
                "coding",
                "--target-dir",
                str(target_dir),
                "--agents",
                "augment",
                "--activate",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Skipped activation for unverified adapters: augment", result.stdout)
            self.assertTrue((target_dir / ".dprofile/generated/augment/INSTRUCTIONS.md").is_file())
            self.assertFalse((target_dir / ".augment").exists())

    def test_apply_refuses_to_overwrite_unmanaged_activated_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles_dir = root / "profiles"
            target_dir = root / "project"
            target_dir.mkdir()
            write_profile(profiles_dir, "coding", "implementation")
            (target_dir / "CLAUDE.md").write_text("human notes\n", encoding="utf-8")

            result = run_cli(
                profiles_dir,
                "apply",
                "coding",
                "--target-dir",
                str(target_dir),
                "--agents",
                "claude",
                "--activate",
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("refusing to overwrite unmanaged file", result.stderr)
            self.assertEqual((target_dir / "CLAUDE.md").read_text(encoding="utf-8"), "human notes\n")

    def test_init_ai_uses_install_style_adapter_activation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles_dir = root / "profiles"
            target_dir = root / "project"
            target_dir.mkdir()
            write_profile(profiles_dir, "coding", "implementation")

            result = run_cli(
                profiles_dir,
                "init",
                "coding",
                "--target-dir",
                str(target_dir),
                "--ai",
                "codex",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Initialized profile: coding", result.stdout)
            self.assertTrue((target_dir / ".dprofile/generated/codex/AGENTS.md").is_file())
            self.assertIn("implementation", (target_dir / "AGENTS.md").read_text(encoding="utf-8"))
            state = json.loads((target_dir / ".dprofile/state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["adapters"], ["codex"])
            self.assertEqual(state["activated_files"], ["AGENTS.md"])

    def test_init_ai_unverified_generates_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles_dir = root / "profiles"
            target_dir = root / "project"
            target_dir.mkdir()
            write_profile(profiles_dir, "coding", "implementation")

            result = run_cli(
                profiles_dir,
                "init",
                "coding",
                "--target-dir",
                str(target_dir),
                "--ai",
                "augment",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Skipped activation for unverified adapters: augment", result.stdout)
            self.assertTrue((target_dir / ".dprofile/generated/augment/INSTRUCTIONS.md").is_file())
            self.assertFalse((target_dir / ".augment").exists())

    def test_cursor_adapter_uses_mdc_frontmatter_and_operating_protocol_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles_dir = root / "profiles"
            target_dir = root / "project"
            target_dir.mkdir()
            write_profile(profiles_dir, "coding", "implementation")

            result = run_cli(
                profiles_dir,
                "apply",
                "coding",
                "--target-dir",
                str(target_dir),
                "--agents",
                "cursor",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            content = (target_dir / ".dprofile/generated/cursor/dprofile.mdc").read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---\n"))
            self.assertIn("alwaysApply: true", content)
            self.assertIn("## Operating Protocol", content)
            self.assertNotIn("## User Context", content)
            self.assertNotIn("## Agent Identity", content)

    def test_copilot_adapter_uses_project_instructions_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles_dir = root / "profiles"
            target_dir = root / "project"
            target_dir.mkdir()
            write_profile(profiles_dir, "coding", "implementation")

            result = run_cli(
                profiles_dir,
                "apply",
                "coding",
                "--target-dir",
                str(target_dir),
                "--agents",
                "copilot",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            content = (target_dir / ".dprofile/generated/copilot/copilot-instructions.md").read_text(encoding="utf-8")
            self.assertIn("# GitHub Copilot Instructions", content)
            self.assertIn("## Operating Protocol", content)
            self.assertNotIn("## User Context", content)
            self.assertNotIn("## Agent Identity", content)

    def test_codex_adapter_limits_persona_to_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles_dir = root / "profiles"
            target_dir = root / "project"
            target_dir.mkdir()
            write_profile(profiles_dir, "coding", "implementation")

            result = run_cli(
                profiles_dir,
                "apply",
                "coding",
                "--target-dir",
                str(target_dir),
                "--agents",
                "codex",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            content = (target_dir / ".dprofile/generated/codex/AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("# AGENTS.md", content)
            self.assertIn("Active dprofile: coding", content)
            self.assertIn("## Operating Protocol", content)
            self.assertNotIn("## User Context", content)
            self.assertNotIn("## Agent Identity", content)

    def test_claude_adapter_includes_all_profile_layers(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles_dir = root / "profiles"
            target_dir = root / "project"
            target_dir.mkdir()
            write_profile(profiles_dir, "coding", "implementation")

            result = run_cli(
                profiles_dir,
                "apply",
                "coding",
                "--target-dir",
                str(target_dir),
                "--agents",
                "claude",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            content = (target_dir / ".dprofile/generated/claude/CLAUDE.md").read_text(encoding="utf-8")
            self.assertIn("## User Context", content)
            self.assertIn("## Agent Identity", content)
            self.assertIn("## Operating Protocol", content)

    def test_unverified_adapter_marks_manual_activation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles_dir = root / "profiles"
            target_dir = root / "project"
            target_dir.mkdir()
            write_profile(profiles_dir, "coding", "implementation")

            result = run_cli(
                profiles_dir,
                "apply",
                "coding",
                "--target-dir",
                str(target_dir),
                "--agents",
                "augment",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            content = (target_dir / ".dprofile/generated/augment/INSTRUCTIONS.md").read_text(encoding="utf-8")
            self.assertIn("Manual activation required", content)
            self.assertIn("## User Context", content)
            self.assertIn("## Agent Identity", content)
            self.assertIn("## Operating Protocol", content)

    def test_top_level_help_explains_switch_init_apply_split(self) -> None:
        result = run_raw_cli("--help")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Primary workflow lives in SKILL.md", result.stdout)
        self.assertIn("Agent config targets", result.stdout)
        self.assertIn("Code project targets", result.stdout)
        self.assertIn("switch", result.stdout)
        self.assertIn("init", result.stdout)
        self.assertIn("apply", result.stdout)

    def test_init_help_explains_adapter_layer_compatibility(self) -> None:
        result = run_raw_cli("init", "--help")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Claude/Gemini receive full profile context", result.stdout)
        self.assertIn("Cursor/Copilot/Codex/OpenCode receive operating protocol", result.stdout)
        self.assertIn("Unverified adapters generate only", result.stdout)

    def test_guide_command_outputs_agent_usage_protocol(self) -> None:
        result = run_raw_cli("guide")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("dprofile usage guide", result.stdout)
        self.assertIn("SKILL.md is the primary Agent workflow", result.stdout)
        self.assertIn("Use switch for Agent-owned config directories", result.stdout)
        self.assertIn("Use init for code projects", result.stdout)
        self.assertIn("dprofile init coding --target-dir . --ai codex", result.stdout)


if __name__ == "__main__":
    unittest.main()
