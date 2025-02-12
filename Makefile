venv:
	@source .venv/bin/activate

build:
	@uv pip install -e .

run:
	@uv run python -m api