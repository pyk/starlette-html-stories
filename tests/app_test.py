"""StoriesApp integration tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from starlette.testclient import TestClient

from starlette_html_stories import StoriesApp

if TYPE_CHECKING:
    from pathlib import Path

OK = 200


def test_stories_app_renders_story_and_story_local_routes(tmp_path: Path) -> None:
    """Stories can render HTMX URLs backed by story-local Starlette routes."""
    story_file = tmp_path / "search_stories.py"
    story_file.write_text(
        """from starlette.routing import Route
from starlette_html import HTML, button, div
from starlette_html_stories import stories, story


def SearchBox(*, hx_get):
    return button("Search", hx_get=hx_get, hx_target="#results")


async def search_results(request):
    return HTML(div("Mocked search results", id="results"))


stories(title="Design System/SearchBox", component=SearchBox)


# Demonstrates SearchBox with a mocked HTMX endpoint.
@story(routes=[Route("/search", search_results, name="search")])
def WithHtmx(ctx):
    return SearchBox(hx_get=ctx.url_for("search"))
""",
        encoding="utf-8",
    )
    client = TestClient(StoriesApp(directory=tmp_path))

    iframe = client.get("/iframe/design-system-search-box--with-htmx")
    local_route = client.get(
        "/iframe/design-system-search-box--with-htmx/routes/search"
    )

    assert iframe.status_code == OK
    assert (
        'hx-get="http://testserver/iframe/'
        'design-system-search-box--with-htmx/routes/search"'
    ) in iframe.text
    assert "Demonstrates SearchBox with a mocked HTMX endpoint." in iframe.text
    assert local_route.status_code == OK
    assert local_route.text == '<div id="results">Mocked search results</div>'
