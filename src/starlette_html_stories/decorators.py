"""Decorators used by story modules."""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, overload

from starlette_html_stories.core import StoryMeta

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

    from starlette.routing import BaseRoute


@dataclass(slots=True)
class StoryOptions:
    """Metadata attached to a decorated story function."""

    name: str | None = None
    args: Mapping[str, object] = field(default_factory=dict)
    docs: str | None = None
    routes: Sequence[BaseRoute] = field(default_factory=tuple)
    parameters: Mapping[str, object] = field(default_factory=dict)
    tags: Sequence[str] = field(default_factory=tuple)


_MODULE_META: dict[str, StoryMeta] = {}


def stories(
    *,
    title: str,
    component: Callable[..., object] | None = None,
    docs: str | None = None,
    parameters: Mapping[str, object] | None = None,
) -> StoryMeta:
    """Register metadata for the current story module."""
    module_name = _caller_module_name()
    meta = StoryMeta(
        title=title,
        component=component,
        docs=docs,
        parameters=parameters or {},
    )
    _MODULE_META[module_name] = meta
    return meta


@overload
def story(func: Callable[..., object], /) -> Callable[..., object]: ...


@overload
def story(
    func: None = None,
    /,
    *,
    name: str | None = None,
    args: Mapping[str, object] | None = None,
    docs: str | None = None,
    routes: Sequence[BaseRoute] | None = None,
    parameters: Mapping[str, object] | None = None,
    tags: Sequence[str] | None = None,
) -> Callable[[Callable[..., object]], Callable[..., object]]: ...


def story(  # noqa: PLR0913
    func: Callable[..., object] | None = None,
    /,
    *,
    name: str | None = None,
    args: Mapping[str, object] | None = None,
    docs: str | None = None,
    routes: Sequence[BaseRoute] | None = None,
    parameters: Mapping[str, object] | None = None,
    tags: Sequence[str] | None = None,
) -> Callable[..., object] | Callable[[Callable[..., object]], Callable[..., object]]:
    """Mark a function as a story.

    The decorator supports both ``@story`` and ``@story(...)`` forms.
    """

    def decorate(target: Callable[..., object]) -> Callable[..., object]:
        options = StoryOptions(
            name=name,
            args=args or {},
            docs=docs,
            routes=routes or (),
            parameters=parameters or {},
            tags=tags or (),
        )
        setattr(target, "__starlette_html_story__", options)  # noqa: B010
        return target

    if func is not None:
        return decorate(func)
    return decorate


def get_module_meta(module_name: str) -> StoryMeta | None:
    """Return registered metadata for a story module."""
    return _MODULE_META.get(module_name)


def clear_module_meta(module_name: str) -> None:
    """Clear stale metadata before re-importing a story module."""
    _MODULE_META.pop(module_name, None)


def _caller_module_name() -> str:
    frame = inspect.currentframe()
    if frame is None or frame.f_back is None or frame.f_back.f_back is None:
        msg = "stories() could not determine the calling module"
        raise RuntimeError(msg)
    caller = frame.f_back.f_back
    module_name = caller.f_globals.get("__name__")
    if not isinstance(module_name, str):
        msg = "stories() could not determine the calling module name"
        raise TypeError(msg)
    return module_name
