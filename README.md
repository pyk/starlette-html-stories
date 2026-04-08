# starlette-html-stories

`starlette-html-stories` provides development tools for documenting, previewing,
and testing [`starlette-html`](https://github.com/pyk/starlette-html) components
in [Starlette](https://starlette.dev/) apps.

It gives you a simple way to:

- collect component examples in one place
- document design-system usage next to the component examples
- render stories as isolated Starlette pages during development
- pass example data as regular Python arguments
- add story-local routes for HTMX interactions

The goal is to make your app UI easier to discover, reuse, and keep consistent
as it grows.

You might also like my other Starlette packages that I use and maintain:

| Package                                                                 | Description                 |
| ----------------------------------------------------------------------- | --------------------------- |
| [`starlette-html`](https://github.com/pyk/starlette-html)               | Python-first HTML DSL       |
| [`starlette-hot-reload`](https://github.com/pyk/starlette-hot-reload)   | Hot reload for static files |
| [`starlette-tailwindcss`](https://github.com/pyk/starlette-tailwindcss) | Tailwind CSS integration    |

## Installation

```shell
uv add starlette-html-stories
# or
pip install starlette-html-stories
```

## Usage

### Step 1: Compose `html_stories` in lifespan

`html_stories` only activates when `app.debug` is `True`.

```python
from contextlib import asynccontextmanager

from starlette.applications import Starlette
from starlette_html_stories import html_stories

@asynccontextmanager
async def lifespan(app: Starlette):
    async with html_stories(
        app=app,
        directory="src/app/ui/stories",
    ):
        yield


app = Starlette(debug=True, routes=[...], lifespan=lifespan)
```

Then open `/__stories__/` in your browser.

### Step 2: Write a component story

Stories are plain Python functions.

```python
from app.ui.components import UserCard
from starlette_html_stories import stories, story

stories(title="Design System/UserCard", component=UserCard)

# Shows the default user card state used across the app.
@story(args={"user": {"name": "Ada", "email": "ada@example.com"}})
def Default(args):
    return UserCard(user=args["user"])
```

The leading comment is used as story documentation. You can also use a function
docstring or pass `docs=` explicitly.

```python
@story(args={"user": {"name": "Grace", "email": "grace@example.com"}})
def GraceHopper(args):
    """Shows a second user fixture for documentation and visual checks."""
    return UserCard(user=args["user"])
```

## Preview Layout

Use `preview_layout` when stories should use your app shell, global CSS, or
design-system layout.

```python
from contextlib import asynccontextmanager
from functools import partial

from app.ui.layouts import BaseLayout
from starlette_html_stories import html_stories


@asynccontextmanager
async def lifespan(app):
    async with html_stories(
        app=app,
        directory="src/app/ui/stories",
        preview_layout=partial(BaseLayout, page_title="Stories"),
    ):
        yield
```

This keeps each story focused on the component:

```python
@story(args={"user": {"name": "Ada", "email": "ada@example.com"}})
def Default(args):
    return UserCard(user=args["user"])
```

## HTMX-Friendly Stories

Story-local routes make interactive examples possible without wiring a story to
your real business logic.

Use `ctx.url_for(...)` to point HTMX attributes at a route owned by the current
story.

```python
@story(routes=[Route("/load-more", load_more, name="load_more")])
def WithLoadMore(ctx):
    return Feed(
        hx_get=ctx.url_for("load_more"),
        hx_target="#feed",
    )
```

## Example App

The repository includes a basic example.

```shell
uv run uvicorn examples.basic:app --reload
```

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/__stories__/`

## Development

Run the development server when working on `starlette-html-stories` itself:

```shell
just dev
```

This starts `tools/app.py`, which uses the dev-only `starlette-tailwindcss`
dependency to build and watch `tools/styles.css`. The generated CSS is written
to `src/starlette_html_stories/static/stories.css`, ignored by git, and bundled
with the published package.

For release, run:

```shell
just build
uv publish
```

## License

MIT
