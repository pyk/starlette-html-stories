"""Shared Tailwind CSS build settings for maintainer tooling."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from starlette_tailwindcss import tailwind

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

ROOT = Path(__file__).resolve().parent.parent
STYLES = ROOT / "tools" / "styles.css"
BUNDLED_CSS = ROOT / "src" / "starlette_html_stories" / "static" / "stories.css"


@asynccontextmanager
async def build_css(*, watch: bool) -> AsyncIterator[None]:
    """Build the bundled CSS once or keep watching for changes."""
    async with tailwind(
        watch=watch,
        version="v4.2.2",
        input=STYLES,
        output=BUNDLED_CSS,
    ):
        yield
