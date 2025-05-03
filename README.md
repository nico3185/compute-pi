# Compute Pi

A high-precision π calculator using the Chudnovsky algorithm.

## Features

- High-precision π calculation using the Chudnovsky algorithm
- Progress tracking with tqdm
- Comprehensive logging
- Result validation
- Docker support

## Installation

### Using pip

```bash
pip install compute-pi
```

### Using Docker

```bash
# Pull from GitHub Container Registry
docker pull ghcr.io/nico3185/compute-pi:latest

# Run container with default settings (precision 1000)
docker run ghcr.io/nico3185/compute-pi:latest

# Run with custom precision
docker run ghcr.io/nico3185/compute-pi:latest --precision 5000 --show-digits 100
```

### From Source

```bash
git clone https://github.com/yourusername/compute-pi.git
cd compute-pi
pip install -e .
```

## Usage

### Command Line

```bash
# Calculate π to 1000 decimal places
compute-pi --precision 1000

# Calculate π to 100 decimal places and show only first 50 digits
compute-pi --precision 100 --show-digits 50

# Calculate without progress bar
compute-pi --precision 1000 --no-progress

# Enable verbose output
compute-pi --precision 1000 --verbose

# Save logs to file
compute-pi --precision 1000 --log-file compute_pi.log
```

### Python API

```python
from compute_pi import PiCalculator

# Create calculator instance
calculator = PiCalculator(precision=1000)

# Compute π
result = calculator.compute_pi()

# Format and print result
print(calculator.format_result(result))
```

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run tests with coverage
pytest tests/ --cov=compute_pi

# Run benchmarks
pytest tests/ --benchmark-only
```

### Docker Development

```bash
# Build image locally
docker compose build

# Run tests in container
docker compose run --rm dev

# Run application with default settings
docker compose run --rm app

# Run with custom parameters
docker compose run --rm app compute-pi --precision 2000 --show-digits 100

# Run all checks (formatting, linting, testing, coverage)
docker compose run --rm test

# Use prebuilt development image
docker pull ghcr.io/nico3185/compute-pi:dev
docker run --rm ghcr.io/nico3185/compute-pi:dev pytest
```

## License

MIT License
