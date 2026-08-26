import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from suoyin.cli import build_manifest_for_paths, main


class BuildManifestForPathsTest(unittest.TestCase):
    def test_single_directory_keeps_directory_relative_paths(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src"
            package = src / "pkg"
            package.mkdir(parents=True)
            (package / "__init__.py").write_text("", encoding="utf-8")
            (package / "module.py").write_text(
                "def alpha() -> None:\n    pass\n",
                encoding="utf-8",
            )

            manifest = build_manifest_for_paths(["src"], root)

            self.assertIn("## pkg/module.py", manifest)
            self.assertNotIn("## src/pkg/module.py", manifest)

    def test_multiple_files_work_like_shell_expansion(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "alpha.py").write_text(
                "def alpha() -> None:\n    pass\n",
                encoding="utf-8",
            )
            (root / "beta.py").write_text(
                "def beta() -> None:\n    pass\n",
                encoding="utf-8",
            )

            manifest = build_manifest_for_paths(["alpha.py", "beta.py"], root)

            self.assertIn("## alpha.py", manifest)
            self.assertIn("## beta.py", manifest)

    def test_recursive_globs_are_expanded_relative_to_cwd(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            package = root / "src" / "pkg"
            package.mkdir(parents=True)
            (package / "__init__.py").write_text("", encoding="utf-8")
            (package / "module.py").write_text(
                "def alpha() -> None:\n    pass\n",
                encoding="utf-8",
            )

            manifest = build_manifest_for_paths(["src/**/*.py"], root)

            self.assertIn("## src/pkg/__init__.py", manifest)
            self.assertIn("## src/pkg/module.py", manifest)


class MainTest(unittest.TestCase):
    def test_invalid_path_specs_are_reported_without_traceback(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = [
                (str(root / "missing.py"), "Path does not exist:"),
                (str(root / "*.py"), "No paths matched:"),
            ]

            for path_spec, expected_error in cases:
                with self.subTest(path_spec=path_spec):
                    stderr = StringIO()
                    with (
                        patch("sys.argv", ["suoyin", path_spec]),
                        redirect_stderr(stderr),
                        self.assertRaises(SystemExit) as raised,
                    ):
                        main()

                    message = stderr.getvalue()
                    self.assertEqual(raised.exception.code, 2)
                    self.assertIn("usage: suoyin [-h] [--version] [paths ...]", message)
                    self.assertIn(
                        f"suoyin: error: {expected_error} {path_spec}", message
                    )
                    self.assertNotIn("Traceback", message)


if __name__ == "__main__":
    unittest.main()
