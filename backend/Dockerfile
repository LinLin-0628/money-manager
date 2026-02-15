# Stage 1: Build stage
FROM python:3.13-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy only dependency files for better caching
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
# --frozen ensures uv.lock is not updated
# --no-dev excludes development dependencies
# --no-install-project skips installing the project itself as a package
RUN uv sync --frozen --no-dev --no-install-project

# Stage 2: Runtime stage
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_ENV=production \
    PATH="/app/.venv/bin:$PATH"

# Create a non-root user
RUN groupadd -g 1000 appuser && \
    useradd -r -u 1000 -g appuser appuser

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code and necessary files
COPY app/ ./app/
COPY migrations/ ./migrations/
COPY main.py alembic.ini config.yaml ./

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose the default FastAPI port
EXPOSE 8000

# Command to run migrations and start the server
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
