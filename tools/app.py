"""Maintainer development server for starlette-html-stories."""

from __future__ import annotations

import logging
import sys
from contextlib import AsyncExitStack, asynccontextmanager
from typing import TYPE_CHECKING

from starlette.applications import Starlette
from starlette_hot_reload import hot_reload

from starlette_html_stories import html_stories
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
    """Build CSS, attach stories routes, and enable browser hot reload."""
    async with AsyncExitStack() as stack:
        await stack.enter_async_context(build_css(watch=app.debug))
        await stack.enter_async_context(
            html_stories(
                app=app,
                directory=ROOT / "tools" / "stories",
                mount_path="/",
            )
        )
        await stack.enter_async_context(
            hot_reload(
                app=app,
                watch_dirs=[ROOT / "tools", ROOT / "src" / "starlette_html_stories"],
            )
        )
        yield


app = Starlette(
    debug=True,
    lifespan=lifespan,
)
