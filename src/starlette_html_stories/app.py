"""Starlette ASGI application for browsing stories."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.routing import Route, Router
from starlette_html import (
    Document,
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
    from collections.abc import Iterable
    from pathlib import Path

    from starlette.requests import Request
    from starlette.types import Message, Receive, Scope, Send


class StoriesApp:
    """ASGI sub-application that serves discovered starlette-html stories."""

    def __init__(
        self,
        *,
        directory: str | Path,
        title: str = "starlette-html-stories",
    ) -> None:
        """Create a stories app from a story directory."""
        self.title = title
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
                    style(_INDEX_CSS),
                ),
                body(h1(self.title), *content),
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
        return Document(
            html(
                head(
                    page_title(f"{story.title} - {story.name}"),
                    style(_IFRAME_CSS),
                ),
                body(docs, main(result)),
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
                status_code = cast("int", message["status"])
                headers = cast("list[tuple[bytes, bytes]]", message["headers"])
            elif message["type"] == "http.response.body":
                body.extend(cast("bytes", message.get("body", b"")))

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
        h2(group_title),
        ul(
            [
                li(
                    a(
                        story.name,
                        href=request.url_for("story_iframe", story_id=story.id),
                    )
                )
                for story in stories
            ]
        ),
    )


_INDEX_CSS = (
    "body{font-family:system-ui,sans-serif;margin:2rem;line-height:1.5}"
    "a{color:#2563eb;text-decoration:none}"
    "a:hover{text-decoration:underline}"
)

_IFRAME_CSS = (
    "body{font-family:system-ui,sans-serif;margin:2rem}"
    ".story-docs{color:#475569;margin-bottom:1.5rem;white-space:pre-wrap}"
)
