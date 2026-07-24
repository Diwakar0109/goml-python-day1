# Use Python 3.13 slim image
FROM python:3.13-slim

# Set runtime environment variables
# - PYTHONUNBUFFERED=1: ensures stdout/stderr are unbuffered
# - PYTHONDONTWRITEBYTECODE=1: prevents creation of .pyc files
# - PATH: prepends virtual environment binaries path so we don't need 'uv run' prefix
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Copy the pre-compiled uv binary from its official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory inside the container
WORKDIR /app

# Create a non-privileged system user for security
RUN adduser --disabled-password --gecos "" appuser

# Copy dependency configuration files first to cache dependencies layer
COPY pyproject.toml uv.lock ./

# Synchronize dependencies only (excludes the project itself and dev packages)
RUN uv sync --frozen --no-dev --no-install-project

# Copy the rest of the application files and assign ownership to appuser
COPY --chown=appuser:appuser . .

# Complete the synchronization including project setup
RUN uv sync --frozen --no-dev

# Grant executable permission to the entrypoint script
RUN chmod +x entrypoint.sh

# Switch to the non-privileged user
USER appuser

# Expose the application port
EXPOSE 8000

# Run the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
