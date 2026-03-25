import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from suoyin.cli import build_manifest_for_paths


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


if __name__ == "__main__":
    unittest.main()
