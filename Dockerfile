# syntax=docker/dockerfile:1.4

FROM python:3.9-slim AS base
WORKDIR /app

# Copy only the necessary files
COPY pyproject.toml README.md ./
COPY compute_pi ./compute_pi

FROM base AS dev
COPY tests ./tests
RUN pip install --no-cache-dir .[dev] && \
    pytest tests/

FROM base AS prod
RUN pip install --no-cache-dir .
ENTRYPOINT ["compute-pi"]

# Default command (can be overridden)
CMD ["--precision", "1000"] 