"""
suoyin.cli

Generate a compact Python symbol manifest.

- Recursively scans a target directory
- Respects .gitignore and .ignore
- Skips test modules
- Outputs a compact Markdown index to stdout
- Designed for LLM agent context (high signal, low noise)

Usage:
    uv run suoyin
    uv run suoyin path/to/project
    uvx suoyin
"""

import argparse
import ast
import fnmatch
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

from suoyin import __version__

# Fallback ignores if no ignore files exist
DEFAULT_IGNORES = [
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
    "dist",
    "build",
]


@dataclass(slots=True)
class FunctionSymbol:
    signature: str
    line_no: int


@dataclass(slots=True)
class MemberSymbol:
    name: str
    signature: str
    line_no: int


@dataclass(slots=True)
class ClassSymbol:
    name: str
    line_no: int
    members: list[MemberSymbol] = field(default_factory=list)
    functions: list[FunctionSymbol] = field(default_factory=list)


@dataclass(slots=True)
class ModuleSymbol:
    module: str
    path: str
    classes: list[ClassSymbol]
    functions: list[FunctionSymbol]


def load_ignore_patterns(root: Path) -> list[str]:
    patterns: list[str] = []

    for name in [".gitignore", ".ignore"]:
        path = root / name
        if path.exists():
            patterns.extend(
                line.strip()
                for line in path.read_text().splitlines()
                if line.strip() and not line.startswith("#")
            )

    return patterns or DEFAULT_IGNORES


def is_ignored(path: Path, patterns: list[str]) -> bool:
    path_str = str(path)
    return any(
        fnmatch.fnmatch(path_str, pattern)
        or any(fnmatch.fnmatch(part, pattern) for part in path.parts)
        for pattern in patterns
    )


def is_test_path(path: Path) -> bool:
    if path.name == "conftest.py":
        return True

    if any(part in {"test", "tests"} for part in path.parts):
        return True

    stem = path.stem
    return stem.startswith("test_") or stem.endswith(("_test", "_tests"))


def format_node(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:
        return "..."


def format_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef, *, is_async: bool
) -> str:
    prefix = "async def" if is_async else "def"
    arguments = format_node(node.args)
    returns = f" -> {format_node(node.returns)}" if node.returns else ""
    return f"{prefix} {node.name}({arguments}){returns}"


def format_member(name: str, annotation: ast.expr | None) -> str:
    if annotation is None:
        return name
    return f"{name}: {format_node(annotation)}"


def attribute_name(target: ast.expr) -> str:
    if not isinstance(target, ast.Attribute):
        return ""
    if not isinstance(target.value, ast.Name):
        return ""
    if target.value.id != "self":
        return ""
    return target.attr


def assigned_names(target: ast.expr) -> list[str]:
    if isinstance(target, ast.Name):
        return [target.id]

    if isinstance(target, ast.Tuple | ast.List):
        names: list[str] = []
        for element in target.elts:
            names.extend(assigned_names(element))
        return names

    return []


def remember_member(
    members: dict[str, MemberSymbol], name: str, annotation: ast.expr | None, line_no: int
) -> None:
    signature = format_member(name, annotation)
    member = MemberSymbol(name=name, signature=signature, line_no=line_no)
    existing = members.get(name)
    if existing is None:
        members[name] = member
        return

    if ":" not in existing.signature and ":" in signature:
        members[name] = member


def merge_member(members: dict[str, MemberSymbol], member: MemberSymbol) -> None:
    existing = members.get(member.name)
    if existing is None:
        members[member.name] = member
        return

    if ":" not in existing.signature and ":" in member.signature:
        members[member.name] = member


def method_members(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[MemberSymbol]:
    members: dict[str, MemberSymbol] = {}

    for statement in ast.walk(node):
        remember_method_member(members, statement)

    return sorted(members.values(), key=lambda member: member.line_no)


class ManifestVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.classes: list[ClassSymbol] = []
        self.functions: list[FunctionSymbol] = []
        self._class_names: list[str] = []
        self._class_stack: list[ClassSymbol] = []

    def visit(self, node: ast.AST) -> None:
        if isinstance(node, ast.ClassDef):
            self.visit_class_def(node)
            return

        if isinstance(node, ast.FunctionDef):
            self.visit_function_def(node)
            return

        if isinstance(node, ast.AsyncFunctionDef):
            self.visit_async_function_def(node)
            return

        super().visit(node)

    def visit_class_def(self, node: ast.ClassDef) -> None:
        class_symbol = ClassSymbol(
            name=".".join([*self._class_names, node.name]),
            line_no=node.lineno,
            members=class_members(node),
        )
        self.classes.append(class_symbol)
        self._visit_class_body(node, class_symbol)

    def visit_function_def(self, node: ast.FunctionDef) -> None:
        self._handle_function(node, is_async=False)

    def visit_async_function_def(self, node: ast.AsyncFunctionDef) -> None:
        self._handle_function(node, is_async=True)

    def _handle_function(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef, *, is_async: bool
    ) -> None:
        function = FunctionSymbol(
            signature=format_function(node, is_async=is_async),
            line_no=node.lineno,
        )
        if self._class_stack:
            self._class_stack[-1].functions.append(function)
            return
        self.functions.append(function)

    def _visit_class_body(self, node: ast.ClassDef, class_symbol: ClassSymbol) -> None:
        self._class_names.append(node.name)
        self._class_stack.append(class_symbol)
        for statement in node.body:
            if isinstance(statement, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
                self.visit(statement)
        self._class_stack.pop()
        self._class_names.pop()
        class_symbol.functions.sort(key=lambda function: function.line_no)


def remember_method_member(
    members: dict[str, MemberSymbol], statement: ast.stmt | ast.expr
) -> None:
    if isinstance(statement, ast.Assign):
        remember_assignment_members(members, statement)
        return

    if isinstance(statement, ast.AnnAssign):
        remember_attribute_member(
            members,
            statement.target,
            line_no=statement.lineno,
            annotation=statement.annotation,
        )
        return

    if isinstance(statement, ast.AugAssign):
        remember_attribute_member(members, statement.target, line_no=statement.lineno)


def remember_assignment_members(
    members: dict[str, MemberSymbol], statement: ast.Assign
) -> None:
    for target in statement.targets:
        remember_attribute_member(members, target, line_no=statement.lineno)


def remember_attribute_member(
    members: dict[str, MemberSymbol],
    target: ast.expr,
    *,
    line_no: int,
    annotation: ast.expr | None = None,
) -> None:
    name = attribute_name(target)
    if name:
        remember_member(members, name, annotation, line_no)


def remember_class_member(members: dict[str, MemberSymbol], statement: ast.stmt) -> None:
    if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
        remember_member(
            members,
            statement.target.id,
            statement.annotation,
            statement.lineno,
        )
        return

    if isinstance(statement, ast.Assign):
        for target in statement.targets:
            for name in assigned_names(target):
                remember_member(members, name, None, statement.lineno)


def class_members(node: ast.ClassDef) -> list[MemberSymbol]:
    members: dict[str, MemberSymbol] = {}
    for statement in node.body:
        remember_class_member(members, statement)
        if isinstance(statement, ast.FunctionDef | ast.AsyncFunctionDef):
            for member in method_members(statement):
                merge_member(members, member)
    return sorted(members.values(), key=lambda member: member.line_no)


def find_python_files(root: Path, ignores: list[str]) -> Iterator[Path]:
    for path in root.rglob("*.py"):
        relative_path = path.relative_to(root)
        if is_test_path(relative_path):
            continue
        if is_ignored(relative_path, ignores):
            continue
        yield path


def module_name(root: Path, path: Path) -> str:
    rel = path.relative_to(root)
    parts = list(rel.parts)
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    else:
        parts[-1] = parts[-1][:-3]
    return ".".join(parts)


def parse_file(root: Path, path: Path) -> ModuleSymbol | None:
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(path))
    except Exception:
        return None

    visitor = ManifestVisitor()
    visitor.visit(tree)
    visitor.classes.sort(key=lambda symbol: symbol.line_no)
    visitor.functions.sort(key=lambda symbol: symbol.line_no)

    return ModuleSymbol(
        module=module_name(root, path),
        path=str(path.relative_to(root)),
        classes=visitor.classes,
        functions=visitor.functions,
    )


def render(modules: list[ModuleSymbol]) -> str:
    lines = ["# Manifest", ""]
    for module in modules:
        lines.extend(render_module(module))

    return "\n".join(lines)


def render_module(module: ModuleSymbol) -> list[str]:
    lines = [f"## {module.path}"]

    if module.classes:
        lines.append("  classes:")
        for class_symbol in module.classes:
            lines.extend(render_class(class_symbol))

    if module.functions:
        lines.append("  functions:")
        lines.extend(
            f"    - {function.signature} @L{function.line_no}"
            for function in module.functions
        )

    lines.append("")
    return lines


def render_class(class_symbol: ClassSymbol) -> list[str]:
    lines = [f"    - class {class_symbol.name} @L{class_symbol.line_no}"]

    if class_symbol.members:
        lines.append("      members:")
        lines.extend(
            f"        - {member.signature} @L{member.line_no}"
            for member in class_symbol.members
        )

    if class_symbol.functions:
        lines.append("      functions:")
        lines.extend(
            f"        - {function.signature} @L{function.line_no}"
            for function in class_symbol.functions
        )

    return lines


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="suoyin",
        description="Generate a compact Python symbol manifest for a Python project.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Root directory to scan. Defaults to the current working directory.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser.parse_args()


def build_manifest(root: Path) -> str:
    ignores = load_ignore_patterns(root)

    modules: list[ModuleSymbol] = []
    for file in find_python_files(root, ignores):
        parsed = parse_file(root, file)
        if parsed:
            modules.append(parsed)

    modules.sort(key=lambda module: module.module)

    return render(modules)


def main() -> None:
    args = parse_args()
    root = Path(args.path).expanduser().resolve()
    assert root.exists(), f"Path does not exist: {root}"
    assert root.is_dir(), f"Path is not a directory: {root}"
    print(build_manifest(root))


if __name__ == "__main__":
    main()
