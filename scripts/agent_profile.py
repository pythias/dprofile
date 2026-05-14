#!/usr/bin/env python3
"""Compatibility wrapper for local script usage."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_profile.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
