"""User card component for the basic example."""

from starlette_html import article, h2, p


def UserCard(*, user: dict[str, str]) -> object:
    """Render a small card with user details."""
    return article(
        h2(user["name"]),
        p(user["email"]),
        cls="user-card",
    )
