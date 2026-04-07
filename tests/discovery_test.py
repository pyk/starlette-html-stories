"""Story discovery tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from starlette_html_stories import discover_stories

if TYPE_CHECKING:
    from pathlib import Path


def test_discover_stories_collects_decorated_functions_and_comment_docs(
    tmp_path: Path,
) -> None:
    """Discovery should collect decorated stories and nearby comments as docs."""
    story_file = tmp_path / "button_stories.py"
    story_file.write_text(
        """\"\"\"Button module docs.\"\"\"

from starlette_html import button
from starlette_html_stories import stories, story


def Button(*, label):
    \"\"\"Button component docs.\"\"\"
    return button(label)


stories(title="Design System/Button", component=Button)


# Use primary buttons for the main action in a section.
@story(args={"label": "Save"})
def Primary(args):
    return Button(**args)


@story
def WithDocstring():
    \"\"\"Story docstrings work too.\"\"\"
    return Button(label="Docstring")
""",
        encoding="utf-8",
    )

    stories = discover_stories(tmp_path)

    assert [item.id for item in stories] == [
        "design-system-button--primary",
        "design-system-button--with-docstring",
    ]
    assert stories[0].name == "Primary"
    assert stories[0].args == {"label": "Save"}
    assert stories[0].docs == "Use primary buttons for the main action in a section."
    assert stories[1].docs == "Story docstrings work too."
