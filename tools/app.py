"""Maintainer development server for starlette-html-stories."""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from starlette.applications import Starlette

from starlette_html_stories import StoriesApp
from tools.css import ROOT, build_css

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stderr,
)


@asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[None]:
    """Build and watch the bundled stories CSS while the dev app runs."""
    async with build_css(watch=app.debug):
        yield


app = Starlette(
    debug=True,
    lifespan=lifespan,
)
app.mount(
    "/",
    StoriesApp(
        directory=ROOT / "tools" / "stories",
    ),
    name="stories",
)
