"""Maintainer development server for starlette-html-stories."""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from starlette.applications import Starlette
from starlette_tailwindcss import tailwind

from starlette_html_stories import StoriesApp

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


ROOT = Path(__file__).resolve().parent.parent
STYLES = ROOT / "tools" / "styles.css"
BUNDLED_CSS = ROOT / "src" / "starlette_html_stories" / "static" / "stories.css"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stderr,
)


@asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[None]:
    """Build and watch the bundled stories CSS while the dev app runs."""
    async with tailwind(
        watch=app.debug,
        version="v4.2.2",
        input=STYLES,
        output=BUNDLED_CSS,
    ):
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
