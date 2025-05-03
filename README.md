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
docker pull compute-pi
docker run compute-pi --precision 1000
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
# Build image
docker build -t compute-pi .

# Run tests in container
docker run compute-pi python -m pytest tests/
```

## License

MIT License
