"""UserCard stories for the basic example."""

from examples.basic.components import UserCard
from starlette_html_stories import stories, story

stories(title="Basic/UserCard", component=UserCard)


# The default user card documents the simplest happy-path component state.
@story(args={"user": {"name": "Ada", "email": "ada@example.com"}})
def Default(args: dict[str, dict[str, str]]) -> object:
    """Render the user card with example data."""
    return UserCard(user=args["user"])


# This variant gives agents a named example for a different user fixture.
@story(
    name="Grace Hopper",
    args={"user": {"name": "Grace", "email": "grace@example.com"}},
)
def GraceHopper(args: dict[str, dict[str, str]]) -> object:
    """Render the user card with another common fixture."""
    return UserCard(user=args["user"])
