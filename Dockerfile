# syntax=docker/dockerfile:1.4

FROM python:3.9-alpine AS base
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
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && cp /root/.local/bin/uv /usr/local/bin/uv

# Copy only the necessary files
COPY pyproject.toml README.md ./
COPY compute_pi ./compute_pi

FROM python:3.9-alpine AS dev
WORKDIR /app

# Install build and runtime dependencies and uv
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && cp /root/.local/bin/uv /usr/local/bin/uv

# Copy project files
COPY --from=base /app /app
COPY tests ./tests
COPY benchmarks ./benchmarks

# Install dev dependencies from source
RUN export PATH=/root/.cargo/bin:$PATH && uv pip install --system -e ".[dev]"
RUN export PATH=/root/.cargo/bin:$PATH && uv pip install --system pytest
RUN pytest tests/

# Optionally remove build dependencies to slim the image
RUN apk del gcc musl-dev python3-dev libffi-dev openssl-dev

FROM python:3.9-alpine AS prod
WORKDIR /app

# Add metadata labels
LABEL org.opencontainers.image.source=https://github.com/nico3185/compute-pi
LABEL org.opencontainers.image.description="High-precision π calculator using the Chudnovsky algorithm"
LABEL org.opencontainers.image.licenses=MIT

# Install build and runtime dependencies and uv
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && cp /root/.local/bin/uv /usr/local/bin/uv

# Copy only the necessary files
COPY --from=base /app /app

# Install production dependencies from source
RUN export PATH=/root/.cargo/bin:$PATH && uv pip install --system -e .

# Optionally remove build dependencies to slim the image
RUN apk del gcc musl-dev python3-dev libffi-dev openssl-dev

# Set Python to run in unbuffered mode (recommended for containers)
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["compute-pi"]

# Default command (can be overridden)
CMD ["--precision", "1000", "--plain"] 