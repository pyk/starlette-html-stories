"""Basic Starlette app example for starlette-html-stories."""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from functools import partial
from typing import TYPE_CHECKING

from starlette.applications import Starlette
from starlette.routing import Route
from starlette_html import Document

from examples.basic.layouts import BaseLayout
from examples.basic.pages import HomePage
from starlette_html_stories import html_stories

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

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


@asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[None]:
    """Attach stories to the app during development."""
    async with html_stories(
        app=app,
        directory="examples/basic/stories",
        preview_layout=partial(BaseLayout, page_title="Stories"),
    ):
        yield


app = Starlette(
    debug=True,
    routes=routes,
    lifespan=lifespan,
)
