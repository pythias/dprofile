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


if __name__ == "__main__":
    unittest.main()
