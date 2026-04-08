"""Starlette ASGI application for browsing stories."""

from __future__ import annotations

from importlib import resources
from typing import TYPE_CHECKING

from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.routing import Route, Router
from starlette_html import (
    Document,
    Markup,
    a,
    body,
    h1,
    h2,
    head,
    html,
    li,
    main,
    p,
    section,
    style,
    ul,
)
from starlette_html import title as page_title

from starlette_html_stories.core import StoryDefinition, call_story
from starlette_html_stories.discovery import discover_stories

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from pathlib import Path

    from starlette.requests import Request
    from starlette.types import Message, Receive, Scope, Send

type PreviewLayout = Callable[..., object]


class StoriesApp:
    """ASGI sub-application that serves discovered starlette-html stories."""

    def __init__(
        self,
        *,
        directory: str | Path,
        title: str = "starlette-html-stories",
        preview_layout: PreviewLayout | None = None,
    ) -> None:
        """Create a stories app from a story directory."""
        self.title = title
        self.preview_layout = preview_layout
        self.stories = discover_stories(directory)
        self._story_by_id = {story.id: story for story in self.stories}
        self._app = Starlette(
            routes=[
                Route("/", self.index, name="index"),
                Route("/api/stories.json", self.stories_json, name="stories_json"),
                Route("/iframe/{story_id}", self.iframe, name="story_iframe"),
                Route(
                    "/iframe/{story_id}/routes/{route_path:path}",
                    self.story_route,
                    name="story_route",
                ),
            ]
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Serve the wrapped Starlette application."""
        await self._app(scope, receive, send)

    async def index(self, request: Request) -> HTMLResponse:
        """Render the stories navigation page."""
        groups: dict[str, list[StoryDefinition]] = {}
        for story in self.stories:
            groups.setdefault(story.title, []).append(story)

        content: Iterable[object] = (
            _story_group(group_title, stories, request)
            for group_title, stories in groups.items()
        )
        if not groups:
            content = (p("No stories found."),)

        return Document(
            html(
                head(
                    page_title(self.title),
                    style(Markup(_bundled_css())),
                ),
                body(
                    main(
                        h1(self.title, cls="text-3xl font-bold tracking-tight"),
                        *content,
                        cls="mx-auto max-w-5xl space-y-8 p-8",
                    ),
                    cls="bg-slate-50 font-sans leading-6 text-slate-900",
                ),
            )
        )

    async def stories_json(self, _request: Request) -> JSONResponse:
        """Return the story index as JSON."""
        return JSONResponse(
            [
                {
                    "id": story.id,
                    "name": story.name,
                    "title": story.title,
                    "docs": story.docs,
                    "args": story.args,
                    "parameters": story.parameters,
                    "tags": story.tags,
                }
                for story in self.stories
            ]
        )

    async def iframe(self, request: Request) -> Response:
        """Render a story in isolation."""
        story = self._find_story(request)
        result = await call_story(story, request)
        if isinstance(result, Response):
            return result

        docs = section(p(story.docs), cls="story-docs") if story.docs else None
        content = (docs, main(result))
        if self.preview_layout is not None:
            return Document(self.preview_layout(*content))

        return Document(
            html(
                head(
                    page_title(f"{story.title} - {story.name}"),
                    style(Markup(_bundled_css())),
                ),
                body(
                    *content,
                    cls="bg-white p-8 font-sans text-slate-900",
                ),
            )
        )

    async def story_route(self, request: Request) -> Response:
        """Dispatch to a local route owned by the current story."""
        story = self._find_story(request)
        route_path = request.path_params["route_path"]
        app = Router(routes=story.routes)
        scope = dict(request.scope)
        scope["path"] = f"/{route_path}"
        scope["root_path"] = ""
        status_code = 500
        headers: list[tuple[bytes, bytes]] = []
        body = bytearray()

        async def send(message: Message) -> None:
            nonlocal status_code, headers
            if message["type"] == "http.response.start":
                status_code = _message_status(message)
                headers = _message_headers(message)
            elif message["type"] == "http.response.body":
                body.extend(_message_body(message))

        await app(scope, request.receive, send)
        response = Response(bytes(body), status_code=status_code)
        response.raw_headers = headers
        return response

    def _find_story(self, request: Request) -> StoryDefinition:
        story_id = request.path_params["story_id"]
        story = self._story_by_id.get(story_id)
        if story is None:
            msg = f"story not found: {story_id}"
            raise KeyError(msg)
        return story


def _story_group(
    group_title: str,
    stories: list[StoryDefinition],
    request: Request,
) -> object:
    return (
        h2(
            group_title,
            cls="text-sm font-semibold uppercase tracking-wide text-slate-500",
        ),
        ul(
            [
                li(
                    a(
                        story.name,
                        cls=(
                            "block rounded-lg border border-slate-200 bg-white "
                            "px-4 py-3 "
                            "font-medium text-blue-600 shadow-sm transition "
                            "hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700"
                        ),
                        href=_story_path(request, story.id),
                    )
                )
                for story in stories
            ],
            cls="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3",
        ),
    )


def _story_path(request: Request, story_id: str) -> str:
    root_path = str(request.scope.get("root_path", ""))
    return f"{root_path}/iframe/{story_id}"


def _message_status(message: Message) -> int:
    status = message.get("status")
    if isinstance(status, int):
        return status
    msg = "ASGI response start message is missing an integer status"
    raise TypeError(msg)


def _message_headers(message: Message) -> list[tuple[bytes, bytes]]:
    headers = message.get("headers")
    if not isinstance(headers, list):
        msg = "ASGI response start message is missing headers"
        raise TypeError(msg)
    for header in headers:
        if not _is_header_tuple(header):
            msg = "ASGI response start message contains invalid headers"
            raise TypeError(msg)
    return headers


def _message_body(message: Message) -> bytes:
    body = message.get("body", b"")
    if isinstance(body, bytes):
        return body
    msg = "ASGI response body message contains a non-bytes body"
    raise TypeError(msg)


def _is_header_tuple(header: object) -> bool:
    return (
        isinstance(header, tuple)
        and len(header) == _HEADER_ITEM_LENGTH
        and isinstance(header[0], bytes)
        and isinstance(header[1], bytes)
    )


_HEADER_ITEM_LENGTH = 2


def _bundled_css() -> str:
    """Return the generated CSS bundled with the package."""
    css_path = resources.files("starlette_html_stories").joinpath("static/stories.css")
    try:
        css = css_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        msg = "bundled CSS is missing; run `just build` or `just dev` first"
        raise FileNotFoundError(msg) from exc
    return "/* starlette-html-stories CSS is generated by tools/app.py. */\n" + css
