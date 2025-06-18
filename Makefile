.PHONY: help install install-dev sync test test-cov lint format clean build docs serve-docs

help:				## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:			## Install the package (legacy pip method)
	pip install -e .

install-dev:		## Install development dependencies (legacy pip method)
	pip install -e ".[dev,docs]"

sync:				## Sync dependencies with uv (recommended)
	uv sync --extra dev --extra docs

test:				## Run tests
	uv run python -m pytest

test-cov:			## Run tests with coverage
	uv run python -m pytest --cov=gh_oauth_helper --cov-report=html --cov-report=term

lint:				## Run linting tools
	uv run python -m flake8 src tests
	uv run python -m mypy src

format:				## Format code
	uv run python -m black src tests
	uv run python -m isort src tests

clean:				## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:				## Build the package
	python -m build

docs:				## Build documentation
	make html

html:			## Build HTML documentation only
	uv run sphinx-build -b html docs docs/_build/html

serve-docs:			## Serve documentation locally
	cd docs/_build/html && python -m http.server 8000

upload-test:		## Upload to TestPyPI
	python -m twine upload --repository testpypi dist/*

upload:				## Upload to PyPI
	python -m twine upload dist/*

