# suoyin

`suoyin` generates a compact Markdown manifest of Python modules, classes, members, and functions.

It is designed for fast codebase inspection and for feeding a high-signal summary into LLM workflows.

`suoyin` is the Chinese pinyin for `index`. 

Repository: <https://github.com/alexdong/suoyin>

## Features

- Scans project directories, file lists, or glob selections
- Respects `.gitignore` and `.ignore`
- Skips test files and `conftest.py`
- Renders compact function signatures such as `def func(a: int) -> str`
- Expands classes to show both members and methods

## Usage

The block below is generated from the current repository by
`python tools/update_readme.py`.

You can scan a directory or pass Python files and glob patterns such as
`uv run suoyin '*.py'` and `uv run suoyin 'src/**/*.py'`.

<!-- README:USAGE:START -->
```console
$ uvx suoyin
# Manifest

## src/suoyin/__init__.py
  functions:
    - def _git_version() -> str @L8
    - def _installed_version() -> str @L50

## src/suoyin/__main__.py

## src/suoyin/cli.py
  classes:
    - class FunctionSymbol @L48
      members:
        - signature: str @L49
        - line_no: int @L50
    - class MemberSymbol @L54
      members:
        - name: str @L55
        - signature: str @L56
        - line_no: int @L57
    - class ClassSymbol @L61
      members:
        - name: str @L62
        - line_no: int @L63
        - members: list[MemberSymbol] @L64
        - functions: list[FunctionSymbol] @L65
    - class ModuleSymbol @L69
      members:
        - module: str @L70
        - path: str @L71
        - classes: list[ClassSymbol] @L72
        - functions: list[FunctionSymbol] @L73
    - class ManifestVisitor @L189
      members:
        - classes: list[ClassSymbol] @L191
        - functions: list[FunctionSymbol] @L192
        - _class_names: list[str] @L193
        - _class_stack: list[ClassSymbol] @L194
      functions:
        - def __init__(self) -> None @L190
        - def visit(self, node: ast.AST) -> None @L196
        - def visit_class_def(self, node: ast.ClassDef) -> None @L211
        - def visit_function_def(self, node: ast.FunctionDef) -> None @L220
        - def visit_async_function_def(self, node: ast.AsyncFunctionDef) -> None @L223
        - def _handle_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef, *, is_async: bool) -> None @L226
        - def _visit_class_body(self, node: ast.ClassDef, class_symbol: ClassSymbol) -> None @L238
  functions:
    - def load_ignore_patterns(root: Path) -> list[str] @L76
    - def is_ignored(path: Path, patterns: list[str]) -> bool @L91
    - def is_test_path(path: Path) -> bool @L100
    - def format_node(node: ast.AST) -> str @L111
    - def format_function(node: ast.FunctionDef | ast.AsyncFunctionDef, *, is_async: bool) -> str @L118
    - def format_member(name: str, annotation: ast.expr | None) -> str @L127
    - def attribute_name(target: ast.expr) -> str @L133
    - def assigned_names(target: ast.expr) -> list[str] @L143
    - def remember_member(members: dict[str, MemberSymbol], name: str, annotation: ast.expr | None, line_no: int) -> None @L156
    - def merge_member(members: dict[str, MemberSymbol], member: MemberSymbol) -> None @L170
    - def method_members(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[MemberSymbol] @L180
    - def remember_method_member(members: dict[str, MemberSymbol], statement: ast.stmt | ast.expr) -> None @L249
    - def remember_assignment_members(members: dict[str, MemberSymbol], statement: ast.Assign) -> None @L269
    - def remember_attribute_member(members: dict[str, MemberSymbol], target: ast.expr, *, line_no: int, annotation: ast.expr | None=None) -> None @L276
    - def remember_class_member(members: dict[str, MemberSymbol], statement: ast.stmt) -> None @L288
    - def class_members(node: ast.ClassDef) -> list[MemberSymbol] @L304
    - def find_python_files(root: Path, ignores: list[str]) -> Iterator[Path] @L314
    - def module_name(root: Path, path: Path) -> str @L324
    - def parse_file(root: Path, path: Path) -> ModuleSymbol | None @L334
    - def render(modules: list[ModuleSymbol]) -> str @L354
    - def render_module(module: ModuleSymbol) -> list[str] @L362
    - def render_class(class_symbol: ClassSymbol) -> list[str] @L381
    - def parse_args() -> argparse.Namespace @L401
    - def expand_path_spec(path_spec: str, cwd: Path) -> list[Path] @L422
    - def build_manifest(root: Path) -> str @L439
    - def build_manifest_for_paths(path_specs: list[str], cwd: Path) -> str @L453
    - def main() -> None @L502

## tools/update_readme.py
  functions:
    - def parse_args() -> argparse.Namespace @L23
    - def render_usage() -> str @L35
    - def replace_usage_block(readme: str, usage_block: str) -> str @L49
    - def main() -> None @L57
```
<!-- README:USAGE:END -->

## AGENTS.md

You can add the following instructions to an `AGENTS.md` file to force
reuse-first behavior before the model writes new code:

````md
## Reuse First With `suoyin`

Before writing any new code, generate a symbol manifest for the repo or the relevant subtree:

```bash
uvx suoyin .
```

If the repo is large, scan the relevant area first:

```bash
uvx suoyin src
uvx suoyin app
uvx suoyin package_name
```

### Required workflow

1. Run `uvx suoyin` before creating any new module, class, function, or helper.
2. Read the manifest and look for existing symbols with similar names, signatures, or responsibilities.
3. Open and inspect the most relevant existing files before deciding to add new code.
4. Prefer extending, refactoring, or reusing existing code over creating parallel implementations.
5. Do not create near-duplicate helpers, wrappers, adapters, formatters, parsers, validators, or utility modules unless you can clearly justify why reuse is impossible.
6. If similar code already exists, consolidate toward one implementation instead of adding another.
7. When you choose to add a new symbol anyway, state explicitly why the existing symbols are not the right place.

### Output expectations

In your final response, include a short `Reuse audit`:
- which existing symbols or files you checked
- what you reused or modified
- if you added something new, why duplication was avoided

### Anti-duplication rule

Treat duplicated or highly similar code as a design bug. If a new function or class overlaps heavily with an existing one, stop and refactor the existing implementation instead of adding a second version.

Never create a new file until you have checked `uvx suoyin` output and confirmed there is no appropriate existing home for the change.

Any code change that introduces a new top-level symbol without a preceding `Reuse audit` is incomplete.
````

## Build And Publish

```bash
uv build
uv publish
```

If you have not published with `uv` before, configure a PyPI token first.

## Versioning

`suoyin` uses VCS-derived versions.

- The `0.1.0` baseline tag anchors version history without triggering a publish.
- Later commits automatically become `0.1.1.devN`.
- The dev suffix increments with commit distance from the latest release tag.

## GitHub Actions Publishing

This repository also includes an automated publishing workflow in
[`publish.yml`](.github/workflows/publish.yml).

It publishes to PyPI when you push a tag like `v0.1.1`:

```bash
git tag v0.1.1
git push origin v0.1.1
```

The workflow uses a GitHub Actions environment secret named
`PYPI_API_TOKEN` on the `pypi` environment.

Before the first automated release:

1. Create or reuse a PyPI API token.
2. Store it as the `PYPI_API_TOKEN` secret on the `pypi` GitHub environment.

If you use tag-triggered releases, protect tags matching `v*` in GitHub so only
trusted maintainers can create release tags.
