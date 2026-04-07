"""Base layout for the basic example."""

from starlette_html import body, head, html, style, title


def BaseLayout(*children: object, page_title: str) -> object:
    """Render the shared page shell."""
    return html(
        head(
            title(page_title),
            style(
                "body{font-family:system-ui,sans-serif;margin:2rem;line-height:1.5}"
                ".user-card{border:1px solid #cbd5e1;border-radius:0.75rem;"
                "padding:1rem;max-width:24rem}"
                ".user-card h2{margin-top:0}"
            ),
        ),
        body(*children),
    )
