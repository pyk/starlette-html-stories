check:
    uv run ruff check
    uv run ty check

dev:
    uv run uvicorn tools.app:app --reload --host 0.0.0.0

fmt:
    uv run ruff format .

test:
    uv run pytest
