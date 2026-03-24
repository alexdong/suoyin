from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from subprocess import CalledProcessError, run

__all__ = ["__version__"]


def _git_version() -> str:
    root = Path(__file__).resolve().parents[2]
    if not (root / ".git").exists():
        return ""

    try:
        tag = run(
            [
                "git",
                "describe",
                "--tags",
                "--abbrev=0",
                "--match",
                "[0-9]*",
                "--match",
                "v[0-9]*",
            ],
            capture_output=True,
            check=True,
            cwd=root,
            text=True,
        ).stdout.strip()
        distance = int(
            run(
                ["git", "rev-list", "--count", f"{tag}..HEAD"],
                capture_output=True,
                check=True,
                cwd=root,
                text=True,
            ).stdout.strip()
        )
    except (CalledProcessError, ValueError):
        return ""

    base = tag.removeprefix("v")
    if distance == 0:
        return base

    major, minor, patch = base.split(".")
    return f"{major}.{minor}.{int(patch) + 1}.dev{distance}"


def _installed_version() -> str:
    try:
        return version("suoyin")
    except PackageNotFoundError:
        return ""


__version__ = _git_version() or _installed_version() or "0.0.0"
