# suoyin

`suoyin` generates a compact Markdown manifest of Python modules, classes, members, and functions.

It is designed for fast codebase inspection and for feeding a high-signal summary into LLM workflows.

Repository: <https://github.com/alexdong/suoyin>

## Features

- Recursively scans a project directory
- Respects `.gitignore` and `.ignore`
- Skips test files and `conftest.py`
- Renders compact function signatures such as `def func(a: int) -> str`
- Expands classes to show both members and methods

## Usage

The block below is generated from the current repository by
`python tools/update_readme.py`.

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
    - class FunctionSymbol @L44
      members:
        - signature: str @L45
        - line_no: int @L46
    - class MemberSymbol @L50
      members:
        - name: str @L51
        - signature: str @L52
        - line_no: int @L53
    - class ClassSymbol @L57
      members:
        - name: str @L58
        - line_no: int @L59
        - members: list[MemberSymbol] @L60
        - functions: list[FunctionSymbol] @L61
    - class ModuleSymbol @L65
      members:
        - module: str @L66
        - path: str @L67
        - classes: list[ClassSymbol] @L68
        - functions: list[FunctionSymbol] @L69
    - class ManifestVisitor @L185
      members:
        - classes: list[ClassSymbol] @L187
        - functions: list[FunctionSymbol] @L188
        - _class_names: list[str] @L189
        - _class_stack: list[ClassSymbol] @L190
      functions:
        - def __init__(self) -> None @L186
        - def visit(self, node: ast.AST) -> None @L192
        - def visit_class_def(self, node: ast.ClassDef) -> None @L207
        - def visit_function_def(self, node: ast.FunctionDef) -> None @L216
        - def visit_async_function_def(self, node: ast.AsyncFunctionDef) -> None @L219
        - def _handle_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef, *, is_async: bool) -> None @L222
        - def _visit_class_body(self, node: ast.ClassDef, class_symbol: ClassSymbol) -> None @L234
  functions:
    - def load_ignore_patterns(root: Path) -> list[str] @L72
    - def is_ignored(path: Path, patterns: list[str]) -> bool @L87
    - def is_test_path(path: Path) -> bool @L96
    - def format_node(node: ast.AST) -> str @L107
    - def format_function(node: ast.FunctionDef | ast.AsyncFunctionDef, *, is_async: bool) -> str @L114
    - def format_member(name: str, annotation: ast.expr | None) -> str @L123
    - def attribute_name(target: ast.expr) -> str @L129
    - def assigned_names(target: ast.expr) -> list[str] @L139
    - def remember_member(members: dict[str, MemberSymbol], name: str, annotation: ast.expr | None, line_no: int) -> None @L152
    - def merge_member(members: dict[str, MemberSymbol], member: MemberSymbol) -> None @L166
    - def method_members(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[MemberSymbol] @L176
    - def remember_method_member(members: dict[str, MemberSymbol], statement: ast.stmt | ast.expr) -> None @L245
    - def remember_assignment_members(members: dict[str, MemberSymbol], statement: ast.Assign) -> None @L265
    - def remember_attribute_member(members: dict[str, MemberSymbol], target: ast.expr, *, line_no: int, annotation: ast.expr | None=None) -> None @L272
    - def remember_class_member(members: dict[str, MemberSymbol], statement: ast.stmt) -> None @L284
    - def class_members(node: ast.ClassDef) -> list[MemberSymbol] @L300
    - def find_python_files(root: Path, ignores: list[str]) -> Iterator[Path] @L310
    - def module_name(root: Path, path: Path) -> str @L320
    - def parse_file(root: Path, path: Path) -> ModuleSymbol | None @L330
    - def render(modules: list[ModuleSymbol]) -> str @L350
    - def render_module(module: ModuleSymbol) -> list[str] @L358
    - def render_class(class_symbol: ClassSymbol) -> list[str] @L377
    - def parse_args() -> argparse.Namespace @L397
    - def build_manifest(root: Path) -> str @L416
    - def main() -> None @L430

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
