"""Story discovery for Python story modules."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import inspect
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from starlette_html_stories.core import StoryDefinition, StoryMeta, story_id
from starlette_html_stories.decorators import (
    StoryOptions,
    clear_module_meta,
    get_module_meta,
)

if TYPE_CHECKING:
    from collections.abc import Iterable
    from types import ModuleType


def discover_stories(directory: str | Path) -> list[StoryDefinition]:
    """Import story modules from a directory and return collected stories."""
    root = Path(directory)
    if not root.exists():
        msg = f"stories directory does not exist: {root}"
        raise FileNotFoundError(msg)
    stories: list[StoryDefinition] = []
    for path in _iter_story_files(root):
        module_name = _module_name_for(path)
        module = _import_module(path, module_name)
        stories.extend(_collect_module_stories(module, path))
    return stories


def _iter_story_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*.py")):
        if path.name == "__init__.py":
            continue
        if path.name.endswith("_stories.py") or path.name.endswith(".stories.py"):
            yield path


def _import_module(path: Path, module_name: str) -> ModuleType:
    clear_module_meta(module_name)
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        msg = f"could not load story module: {path}"
        raise ImportError(msg)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _collect_module_stories(module: ModuleType, path: Path) -> list[StoryDefinition]:
    meta = get_module_meta(module.__name__)
    if meta is None:
        msg = f"story module must call stories(...): {path}"
        raise RuntimeError(msg)
    docs = _DocsSource(path)
    module_docs = meta.docs or inspect.getdoc(module)
    meta = StoryMeta(
        title=meta.title,
        component=meta.component,
        docs=module_docs or inspect.getdoc(meta.component),
        parameters=meta.parameters,
    )
    collected: list[StoryDefinition] = []
    for export_name, value in vars(module).items():
        options = getattr(value, "__starlette_html_story__", None)
        if not isinstance(options, StoryOptions):
            continue
        story_docs = (
            options.docs
            or inspect.getdoc(value)
            or docs.leading_comment_for(export_name)
        )
        display_name = options.name or _display_name(export_name)
        collected.append(
            StoryDefinition(
                id=story_id(meta.title, export_name),
                export_name=export_name,
                name=display_name,
                title=meta.title,
                func=value,
                args=options.args,
                docs=story_docs,
                routes=options.routes,
                parameters={**meta.parameters, **options.parameters},
                tags=options.tags,
                module_name=module.__name__,
            )
        )
    return collected


class _DocsSource:
    """Read source docs that are not available after import."""

    def __init__(self, path: Path) -> None:
        self._comments: dict[str, str] = {}
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        lines = source.splitlines()
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                first_line = node.lineno
                if node.decorator_list:
                    first_line = min(
                        decorator.lineno for decorator in node.decorator_list
                    )
                comment = _leading_comment(lines, first_line)
                if comment:
                    self._comments[node.name] = comment

    def leading_comment_for(self, export_name: str) -> str | None:
        """Return a comment block immediately above a story function."""
        return self._comments.get(export_name)


def _leading_comment(lines: list[str], first_line: int) -> str | None:
    index = first_line - 2
    comments: list[str] = []
    while index >= 0:
        stripped = lines[index].strip()
        if not stripped.startswith("#"):
            break
        comments.append(stripped.removeprefix("#").strip())
        index -= 1
    comments.reverse()
    return "\n".join(comments) or None


def _display_name(export_name: str) -> str:
    words = []
    current = ""
    for char in export_name:
        if char == "_":
            if current:
                words.append(current)
                current = ""
        elif char.isupper() and current and not current[-1].isupper():
            words.append(current)
            current = char
        else:
            current += char
    if current:
        words.append(current)
    return " ".join(word[:1].upper() + word[1:] for word in words) or export_name


def _module_name_for(path: Path) -> str:
    digest = hashlib.sha1(
        str(path.resolve()).encode(),
        usedforsecurity=False,
    ).hexdigest()
    return f"_starlette_html_stories_{digest}"
