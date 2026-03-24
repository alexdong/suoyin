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

```bash
uvx suoyin
uvx suoyin path/to/project
```

Local development:

```bash
uv run suoyin
uv run suoyin ../some-project
uv run python -m suoyin --help
```

## Example

```text
# Manifest

## pkg.module  (pkg/module.py)
  classes:
    - class Widget @L10
      members:
        - name: str @L11
      functions:
        - def render(self) -> str @L14
  functions:
    - def make_widget(name: str) -> Widget @L21
```

## Build And Publish

```bash
uv build
uv publish
```

If you have not published with `uv` before, configure a PyPI token first.
