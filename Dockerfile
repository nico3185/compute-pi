# syntax=docker/dockerfile:1.4

FROM python:3.9-alpine AS builder
WORKDIR /app

# Add metadata labels
LABEL org.opencontainers.image.source=https://github.com/nico3185/compute-pi
LABEL org.opencontainers.image.description="High-precision π calculator using the Chudnovsky algorithm"
LABEL org.opencontainers.image.licenses=MIT

# Install build dependencies and uv
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    curl \
    && pip install --no-cache-dir --upgrade pip wheel \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy only the necessary files
COPY pyproject.toml README.md ./
COPY compute_pi ./compute_pi

# Build the wheel
RUN uv pip wheel --wheel-dir=/app/wheels -e .

FROM python:3.9-alpine AS dev
WORKDIR /app

# Install runtime dependencies and uv
RUN apk add --no-cache libffi curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy project files
COPY --from=builder /app /app
COPY tests ./tests
COPY benchmarks ./benchmarks

# Install from wheel with dev dependencies
RUN uv pip install --upgrade pip && \
    uv pip install --find-links=/app/wheels ".[dev]" && \
    pytest tests/

FROM python:3.9-alpine AS prod
WORKDIR /app

# Add metadata labels
LABEL org.opencontainers.image.source=https://github.com/nico3185/compute-pi
LABEL org.opencontainers.image.description="High-precision π calculator using the Chudnovsky algorithm"
LABEL org.opencontainers.image.licenses=MIT

# Install runtime dependencies and uv
RUN apk add --no-cache libffi curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy only the wheel and install
COPY --from=builder /app/wheels /wheels
RUN uv pip install --upgrade pip && \
    uv pip install --no-index --find-links=/wheels compute-pi && \
    rm -rf /wheels

# Set Python to run in unbuffered mode (recommended for containers)
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["compute-pi"]

# Default command (can be overridden)
CMD ["--precision", "1000", "--plain"] 