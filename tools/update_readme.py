#!/usr/bin/env python3
"""
Update the README usage block from the current repository manifest.

Usage:
    uv run python tools/update_readme.py
    uv run python tools/update_readme.py --check
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from suoyin.cli import build_manifest

START_MARKER = "<!-- README:USAGE:START -->"
END_MARKER = "<!-- README:USAGE:END -->"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Update the README usage block from current suoyin output."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if README.md is out of date.",
    )
    return parser.parse_args()


def render_usage() -> str:
    manifest = build_manifest(ROOT).rstrip()
    return "\n".join(
        [
            START_MARKER,
            "```console",
            "$ uvx suoyin",
            manifest,
            "```",
            END_MARKER,
        ]
    )


def replace_usage_block(readme: str, usage_block: str) -> str:
    assert START_MARKER in readme, f"Missing start marker: {START_MARKER}"
    assert END_MARKER in readme, f"Missing end marker: {END_MARKER}"
    before, remainder = readme.split(START_MARKER, maxsplit=1)
    _, after = remainder.split(END_MARKER, maxsplit=1)
    return f"{before}{usage_block}{after}"


def main() -> None:
    args = parse_args()
    readme_path = ROOT / "README.md"
    current_readme = readme_path.read_text()
    expected_readme = replace_usage_block(current_readme, render_usage())

    if args.check:
        assert current_readme == expected_readme, (
            "README.md is out of date. Run `uv run python tools/update_readme.py`."
        )
        return

    readme_path.write_text(expected_readme)


if __name__ == "__main__":
    main()
