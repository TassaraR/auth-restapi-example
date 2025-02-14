build:
	@uv pip install -e .

run:
	@uv run python -m api

remove-db:
	@rm data/duck.db
