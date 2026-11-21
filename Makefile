.PHONY: codegate

codegate:
	uv run --locked ruff check .
	uv run --locked ruff format --check .
	uv run --locked ty check --error-on-warning
