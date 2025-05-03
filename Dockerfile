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
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.profile \
    && source ~/.profile

# Copy only the necessary files
COPY pyproject.toml README.md ./
COPY compute_pi ./compute_pi

# Build the wheel
RUN if command -v uv >/dev/null 2>&1; then \
        uv pip wheel --wheel-dir=/app/wheels -e .; \
    else \
        pip wheel --no-cache-dir --wheel-dir=/app/wheels -e .; \
    fi

FROM python:3.9-alpine AS dev
WORKDIR /app

# Install runtime dependencies and uv
RUN apk add --no-cache libffi curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.profile \
    && source ~/.profile

# Copy project files
COPY --from=builder /app /app
COPY tests ./tests
COPY benchmarks ./benchmarks

# Install from wheel with dev dependencies
RUN if command -v uv >/dev/null 2>&1; then \
        uv pip install --upgrade pip && \
        uv pip install --find-links=/app/wheels ".[dev]"; \
    else \
        pip install --no-cache-dir --upgrade pip && \
        pip install --no-cache-dir --find-links=/app/wheels ".[dev]"; \
    fi && \
    pytest tests/

FROM python:3.9-alpine AS prod
WORKDIR /app

# Add metadata labels
LABEL org.opencontainers.image.source=https://github.com/nico3185/compute-pi
LABEL org.opencontainers.image.description="High-precision π calculator using the Chudnovsky algorithm"
LABEL org.opencontainers.image.licenses=MIT

# Install runtime dependencies and uv
RUN apk add --no-cache libffi curl \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.profile \
    && source ~/.profile

# Copy only the wheel and install
COPY --from=builder /app/wheels /wheels
RUN if command -v uv >/dev/null 2>&1; then \
        uv pip install --upgrade pip && \
        uv pip install --no-index --find-links=/wheels compute-pi; \
    else \
        pip install --no-cache-dir --upgrade pip && \
        pip install --no-cache-dir --no-index --find-links=/wheels compute-pi; \
    fi && \
    rm -rf /wheels

# Set Python to run in unbuffered mode (recommended for containers)
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["compute-pi"]

# Default command (can be overridden)
CMD ["--precision", "1000", "--plain"] 