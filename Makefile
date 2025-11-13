.PHONY: install lint test run

install:
	pip install -e .[dev]

lint:
	ruff check .

test:
	pytest

run:
	uvicorn app.main:app --reload
