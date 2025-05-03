#!/bin/bash
set -e  # Exit on any error

# Create a fresh virtual environment
echo "Step 1: Creating fresh virtual environment..."
rm -rf .venv-ci-test
uv venv .venv-ci-test

# Activate the virtual environment
echo "Step 2: Activating virtual environment..."
source .venv-ci-test/bin/activate

# Install dependencies exactly as in GitHub CI
echo "Step 3: Installing dependencies..."
uv pip install -e ".[dev]"
uv pip install types-psutil types-tqdm

# Check formatting
echo "Step 4: Checking code formatting with black..."
black . --check

# Check imports - explicitly specify the directories to check and exclude .venv-ci-test
echo "Step 5: Checking import sorting..."
isort compute_pi tests benchmarks --check-only

# Run flake8
echo "Step 6: Running flake8..."
flake8 compute_pi tests benchmarks

# Run mypy with verbose output to see what's failing
echo "Step 7: Running mypy (this is where GitHub CI fails)..."
mypy compute_pi tests benchmarks

# Run tests
echo "Step 8: Running tests..."
pytest --cov=compute_pi --cov-report=term-missing --cov-report=xml

echo "All tests passed! Your code should pass GitHub CI." 