"""User card component for maintainer testing."""

from starlette_html import article, h2, p


def UserCard(*, user: dict[str, str]) -> object:
    """Render a small card with user details."""
    return article(
        h2(user["name"], cls="text-lg font-semibold text-slate-900"),
        p(user["email"], cls="mt-1 text-sm text-slate-600"),
        cls=("max-w-md rounded-lg border border-slate-200 bg-white p-4 shadow-sm"),
    )
