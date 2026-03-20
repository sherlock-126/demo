# Multi-stage build for content generator with LLM providers
FROM python:3.10-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    ffmpeg \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data/scripts /app/data/logs /app/cache /app/output /app/videos

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Volume for persistent data and auth tokens
VOLUME ["/app/data", "/app/.auth"]

# Default command
CMD ["python", "-m", "content_generator.cli", "--help"]