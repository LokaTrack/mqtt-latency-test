# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DATABASE_PATH=/app/data/database.db

# Set work directory
WORKDIR /app

# Create data directory for persistent storage
RUN mkdir -p /app/data

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy poetry configuration files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry install && rm -rf $POETRY_CACHE_DIR

# Copy application code
COPY src/ src/
COPY .env .env

# Expose port 8000
EXPOSE 8000

# Create volume for persistent data
VOLUME ["/app/data"]

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the application using the module with proper configuration
CMD ["poetry", "run", "python", "-m", "src.mqtt_latency_test"]