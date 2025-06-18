.PHONY: help install install-dev test test-cov lint format clean build docs serve-docs

help:				## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:			## Install the package
	pip install -e .

install-dev:		## Install development dependencies
	pip install -e ".[dev,docs]"

test:				## Run tests
	python -m pytest

test-cov:			## Run tests with coverage
	python -m pytest --cov=gh_oauth_helper --cov-report=html --cov-report=term

lint:				## Run linting tools
	python -m flake8 src tests
	python -m mypy src

format:				## Format code
	python -m black src tests
	python -m isort src tests

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
	cd docs && make html

serve-docs:			## Serve documentation locally
	cd docs/_build/html && python -m http.server 8000

upload-test:		## Upload to TestPyPI
	python -m twine upload --repository testpypi dist/*

upload:				## Upload to PyPI
	python -m twine upload dist/*

