"""Page components for the basic example."""

from starlette_html import h1, p

from examples.basic.components import UserCard
from examples.basic.layouts import BaseLayout


def HomePage(*, user: dict[str, str]) -> object:
    """Render the homepage."""
    return BaseLayout(
        h1("starlette-html-stories"),
        p("A normal Starlette page using starlette-html components."),
        UserCard(user=user),
        page_title="Home",
    )
