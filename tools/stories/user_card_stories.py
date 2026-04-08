"""UserCard stories for the maintainer tools app."""

from starlette_html_stories import stories, story
from tools.components import UserCard

stories(title="Tools/UserCard", component=UserCard)


# The default user card gives maintainers a simple component smoke test.
@story(args={"user": {"name": "Ada", "email": "ada@example.com"}})
def Default(args: dict[str, dict[str, str]]) -> object:
    """Render the user card with example data."""
    return UserCard(user=args["user"])


# This variant exercises story naming and a second argument fixture.
@story(
    name="Grace Hopper",
    args={"user": {"name": "Grace", "email": "grace@example.com"}},
)
def GraceHopper(args: dict[str, dict[str, str]]) -> object:
    """Render the user card with another common fixture."""
    return UserCard(user=args["user"])
