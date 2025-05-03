.PHONY: install install-dev clean clean-all lint format check test coverage run docker-build docker-test docker-run docker-push help pre-commit-hook ci-check setup-venv release tag-version

# Variables
PYTHON = python3
UV = uv
VENV_DIR = .venv
PACKAGE_NAME = compute_pi
DOCKER_REGISTRY ?= ghcr.io
DOCKER_USERNAME ?= $(shell git config user.name | tr '[:upper:]' '[:lower:]' | tr -d ' ')
IMAGE_NAME = $(DOCKER_REGISTRY)/$(DOCKER_USERNAME)/compute-pi
VERSION ?= $(shell grep -m 1 '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')

help:
	@echo "Available commands:"
	@echo "  make setup-venv      - Set up UV virtual environment"
	@echo "  make install         - Install production dependencies"
	@echo "  make install-dev     - Install development dependencies"
	@echo "  make clean          - Clean up build artifacts and caches"
	@echo "  make clean-all      - Clean everything including virtual environments"
	@echo "  make lint           - Run all linters"
	@echo "  make format         - Format code with black and isort"
	@echo "  make check          - Run all checks (format, lint, mypy)"
	@echo "  make test           - Run tests"
	@echo "  make coverage       - Run tests with coverage report"
	@echo "  make run            - Run the application"
	@echo "  make docker-build   - Build Docker images"
	@echo "  make docker-test    - Run tests in Docker"
	@echo "  make docker-run     - Run application in Docker"
	@echo "  make docker-push    - Push Docker images to registry"
	@echo "  make pre-commit-hook - Set up pre-commit hook for black"
	@echo "  make ci-check       - Run all checks in sequence (like CI does)"
	@echo "  make tag-version    - Create a git tag for current version"
	@echo "  make release        - Create a new release (bump version, tag, push)"

setup-venv:
	@echo "Creating UV virtual environment..."
	$(UV) venv $(VENV_DIR)
	@echo "Virtual environment created at $(VENV_DIR)"
	@echo "Activate using: source $(VENV_DIR)/bin/activate"

install: setup-venv
	$(UV) pip install -e .

install-dev: setup-venv
	$(UV) pip install -e ".[dev]"
	$(UV) pip install types-psutil types-tqdm  # Install type stubs

clean:
	rm -rf build/ dist/ *.egg-info/ .eggs/ .coverage coverage.xml htmlcov/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -f pytest_output.txt .coverage.*

clean-all: clean
	rm -rf $(VENV_DIR) .venv-ci-test/ .benchmarks/
	rm -f uv.lock

lint: lint-flake8 lint-mypy lint-black lint-isort

lint-flake8:
	flake8 $(PACKAGE_NAME) tests benchmarks

lint-mypy:
	mypy $(PACKAGE_NAME) tests benchmarks

lint-black:
	black --check .

lint-isort:
	isort $(PACKAGE_NAME) tests benchmarks --check-only

format:
	black .
	isort $(PACKAGE_NAME) tests benchmarks

format-check:
	black --check .
	isort $(PACKAGE_NAME) tests benchmarks --check-only

check: format-check lint test

test:
	pytest -v

coverage:
	pytest --cov=$(PACKAGE_NAME) --cov-report=term-missing --cov-report=xml --cov-report=html

run:
	$(PYTHON) -m $(PACKAGE_NAME)

docker-build:
	docker compose build
	docker tag compute-pi:latest $(IMAGE_NAME):latest
	docker tag compute-pi:dev $(IMAGE_NAME):dev

docker-test:
	docker compose run --rm dev pytest -v

docker-run:
	docker compose run --rm app

docker-push:
	@echo "Pushing docker images to $(DOCKER_REGISTRY)"
	docker push $(IMAGE_NAME):latest
	docker push $(IMAGE_NAME):dev

pre-commit-hook:
	echo '#!/bin/sh' > .git/hooks/pre-commit
	echo 'make format' >> .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit

# CI check target - run all checks in sequence to ensure GitHub CI will pass
ci-check:
	@echo "Running all checks sequentially (like GitHub CI)..."
	@echo "Step 1: Setting up environment"
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(UV) venv $(VENV_DIR); \
	fi
	@echo "Step 2: Installing dependencies"
	$(UV) pip install -e ".[dev]"
	$(UV) pip install types-psutil types-tqdm
	@echo "Step 3: Code formatting check"
	black . --check
	isort $(PACKAGE_NAME) tests benchmarks --check-only
	@echo "Step 4: Linting"
	flake8 $(PACKAGE_NAME) tests benchmarks
	@echo "Step 5: Type checking"
	mypy $(PACKAGE_NAME) tests benchmarks
	@echo "Step 6: Running tests"
	pytest -v --cov=$(PACKAGE_NAME) --cov-report=term-missing --cov-report=xml
	@echo "All checks passed! 🎉 GitHub CI should pass as well."

# Create a tag for the current version
tag-version:
	@echo "Tagging version $(VERSION)"
	git tag -a v$(VERSION) -m "Release v$(VERSION)"
	@echo "Tag created. Push with: git push origin v$(VERSION)"

# Release a new version (increments version, creates tag, and pushes)
release:
	@echo "Current version: $(VERSION)"
	@echo "Enter new version (e.g., 0.2.0): " && read new_version && \
	sed -i.bak "s/version = \"$(VERSION)\"/version = \"$${new_version}\"/" pyproject.toml && \
	rm -f pyproject.toml.bak && \
	git add pyproject.toml && \
	git commit -m "Bump version to $${new_version}" && \
	git tag -a v$${new_version} -m "Release v$${new_version}" && \
	git push && git push origin v$${new_version} && \
	echo "Released version $${new_version}"

# Default target
all: help 