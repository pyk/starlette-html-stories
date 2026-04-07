check:
    uv run ruff check
    uv run ty check

fmt:
    uv run ruff format .

test:
    uv run pytest
