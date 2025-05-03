# Compute Pi

A high-precision π calculator using the Chudnovsky algorithm.

## Features

- High-precision π calculation using the Chudnovsky algorithm
- Progress tracking with tqdm
- Comprehensive logging
- Result validation
- Docker support

## Installation

### Using uv

```bash
uv pip install compute-pi
```

### Using Docker

```bash
# Pull from GitHub Container Registry
docker pull ghcr.io/user/compute-pi:latest

# Run with default settings (1000 decimal places)
docker run ghcr.io/user/compute-pi:latest

# Run with custom precision
docker run ghcr.io/user/compute-pi:latest --precision 2000
```

### From Source

```bash
git clone https://github.com/nico3185/compute-pi.git
cd compute-pi
uv pip install -e .
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
uv pip install -e ".[dev]"

# Run tests
pytest tests/

# Run tests with coverage
pytest tests/ --cov=compute_pi

# Run benchmarks
pytest tests/ --benchmark-only
```

### Docker Development

```bash
# Build and test using docker-compose
make docker-build
make docker-test

# Run the application
make docker-run

# Push images to registry (GitHub Packages)
make docker-push
```

## Docker Registry

This project uses GitHub Container Registry (ghcr.io) to publish Docker images. The following images are available:

- `ghcr.io/user/compute-pi:latest` - Production image
- `ghcr.io/user/compute-pi:dev` - Development image with testing tools

To use your own registry:

```bash
# Set custom registry and username
export DOCKER_REGISTRY=my-registry.com
export DOCKER_USERNAME=myuser

# Build and push
make docker-build
make docker-push
```

## CI/CD Pipeline

This project includes a comprehensive CI/CD pipeline using GitHub Actions that:

1. **Testing Stage**:
   - Runs tests on multiple Python versions (3.8, 3.9, 3.10, 3.11)
   - Checks code formatting with Black and isort
   - Performs static type checking with mypy
   - Performs linting with flake8
   - Runs the test suite with coverage reporting

2. **Docker Build Stage**:
   - Builds production and development Docker images
   - Pushes images to GitHub Container Registry (ghcr.io)
   - Supports multi-platform builds (amd64)
   - Performs vulnerability scanning with Trivy
   - Uses build caching for faster builds

3. **Deployment Stage**:
   - Creates GitHub releases for tagged versions
   - Publishes versioned Docker images

### Creating a Release

To create a new release:

```bash
# Create a new version tag and release
make release

# Or just tag the current version
make tag-version
git push origin v0.1.0  # Replace with your version
```

This will trigger the CI/CD pipeline to build and publish Docker images with appropriate version tags.

## License

MIT License
