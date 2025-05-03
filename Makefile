.PHONY: install install-dev clean lint format check test coverage run docker-build docker-test docker-run help

# Variables
PYTHON = python3
UV = uv
PACKAGE_NAME = compute_pi

help:
	@echo "Available commands:"
	@echo "  make install         - Install production dependencies"
	@echo "  make install-dev     - Install development dependencies"
	@echo "  make clean          - Clean up build artifacts and caches"
	@echo "  make lint           - Run all linters"
	@echo "  make format         - Format code with black and isort"
	@echo "  make check          - Run all CI/CD checks (format, lint, tests, coverage)"
	@echo "  make test           - Run tests"
	@echo "  make coverage       - Run tests with coverage report"
	@echo "  make run            - Run the application"
	@echo "  make docker-build   - Build Docker images"
	@echo "  make docker-test    - Run tests in Docker"
	@echo "  make docker-run     - Run application in Docker"

install:
	$(UV) pip install -e .

install-dev:
	$(UV) pip install -e ".[dev]"

clean:
	rm -rf build/ dist/ *.egg-info/ .eggs/ .coverage coverage.xml htmlcov/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

lint: lint-flake8 lint-mypy

lint-flake8:
	flake8 $(PACKAGE_NAME) tests benchmarks

lint-mypy:
	mypy .

format:
	black .
	isort .

format-check:
	black --check .
	isort --check-only .

check: format lint test coverage

test:
	pytest -v

coverage:
	pytest --cov=$(PACKAGE_NAME) --cov-report=term-missing --cov-report=xml --cov-report=html

run:
	$(PYTHON) -m $(PACKAGE_NAME)

docker-build:
	docker compose build

docker-test:
	docker compose run --rm dev pytest -v

docker-run:
	docker compose run --rm app

# Default target
all: help 