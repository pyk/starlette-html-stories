"""Core story data structures and rendering helpers."""

from __future__ import annotations

import inspect
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from starlette.datastructures import URLPath
from starlette.responses import Response
from starlette.routing import BaseRoute, NoMatchFound

if TYPE_CHECKING:
    from starlette.requests import Request

RenderResult = object | Response
StoryCallable = Callable[..., RenderResult]


@dataclass(slots=True)
class StoryMeta:
    """Metadata shared by every story in a story module."""

    title: str
    component: Callable[..., object] | None = None
    docs: str | None = None
    parameters: Mapping[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class StoryDefinition:
    """A collected story function and its metadata."""

    id: str
    export_name: str
    name: str
    title: str
    func: StoryCallable
    args: Mapping[str, object] = field(default_factory=dict)
    docs: str | None = None
    routes: Sequence[BaseRoute] = field(default_factory=tuple)
    parameters: Mapping[str, object] = field(default_factory=dict)
    tags: Sequence[str] = field(default_factory=tuple)
    module_name: str = ""


@dataclass(slots=True)
class StoryContext:
    """Runtime context passed to dynamic story functions."""

    request: Request
    story: StoryDefinition

    def url_for(self, name: str, **path_params: object) -> str:
        """Return a URL for one of the current story's local routes."""
        for route in self.story.routes:
            try:
                url_path = route.url_path_for(name, **path_params)
            except NoMatchFound:
                continue
            route_path = str(url_path).lstrip("/")
            path = _rooted_path(
                self.request,
                f"/iframe/{self.story.id}/routes/{route_path}",
            )
            return str(URLPath(path=path).make_absolute_url(self.request.base_url))
        raise NoMatchFound(name, dict(path_params))


def story_id(title: str, export_name: str) -> str:
    """Build a stable story id from the module title and Python export name."""
    return f"{_slug(_split_words(title))}--{_slug(_split_words(export_name))}"


async def call_story(story: StoryDefinition, request: Request) -> RenderResult:
    """Call a story function with the subset of supported arguments it asks for."""
    ctx = StoryContext(request=request, story=story)
    kwargs: dict[str, object] = {}
    signature = inspect.signature(story.func)
    for name in signature.parameters:
        if name == "args":
            kwargs[name] = dict(story.args)
        elif name == "ctx":
            kwargs[name] = ctx
        elif name == "request":
            kwargs[name] = request
        else:
            msg = (
                f"unsupported story parameter {name!r} in "
                f"{story.title}/{story.export_name}"
            )
            raise TypeError(msg)
    result = story.func(**kwargs)
    if inspect.isawaitable(result):
        result = await result
    return result


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return slug or "story"


def _split_words(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    return value.replace("_", " ")


def _rooted_path(request: Request, path: str) -> str:
    root_path = str(request.scope.get("root_path", ""))
    return f"{root_path}{path}"
