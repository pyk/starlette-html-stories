"""Build the bundled CSS once for maintainer workflows."""

from __future__ import annotations

import asyncio

from tools.css import build_css


async def main() -> None:
    """Generate the bundled CSS used by starlette-html-stories."""
    async with build_css(watch=False):
        pass


if __name__ == "__main__":
    asyncio.run(main())
