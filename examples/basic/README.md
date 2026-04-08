# Basic Example

This example starts from the `starlette-html` basic app shape and adds
`starlette-html-stories`.

## Run

```shell
uv run uvicorn examples.basic:app --reload
```

Open:

- `http://127.0.0.1:8000/` for the normal Starlette page.
- `http://127.0.0.1:8000/__stories__/` for the stories app.

## What It Demonstrates

- a Starlette route returning `Document(...)`
- a reusable Python component in `examples/basic/components`
- a shared layout component in `examples/basic/layouts`
- a page component in `examples/basic/pages`
- decorator-first stories in `examples/basic/stories`
- story docs from leading Python comments
- `html_stories(...)` lifespan composition without a sub-app
- `preview_layout=partial(BaseLayout, page_title="Stories")` for shared story
  preview chrome while keeping stories component-focused
