"""Basic Starlette app example for starlette-html-stories."""

from __future__ import annotations

import logging
import sys
from functools import partial
from typing import TYPE_CHECKING

from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette_html import Document

from examples.basic.layouts import BaseLayout
from examples.basic.pages import HomePage
from starlette_html_stories import StoriesApp

if TYPE_CHECKING:
    from starlette.requests import Request
    from starlette.responses import HTMLResponse


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stderr,
)


async def homepage(_request: Request) -> HTMLResponse:
    """Homepage handler."""
    user = {"name": "Ada", "email": "ada@example.com"}
    return Document(HomePage(user=user))


routes = [
    Route("/", homepage),
]


app = Starlette(
    debug=True,
    routes=routes,
)

if app.debug:
    app.routes.append(
        Mount(
            "/__stories__",
            app=StoriesApp(
                directory="examples/basic/stories",
                preview_layout=partial(BaseLayout, page_title="Stories"),
            ),
            name="stories",
        )
    )
