# Multi-stage Dockerfile for Demo Content Generator
# Stage 1: Builder - Build Python dependencies
FROM python:3.10-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install wheel
RUN pip install --no-cache-dir --upgrade pip wheel setuptools

# Copy requirements and install Python dependencies
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Stage 2: Final image
FROM python:3.10-slim

# Install system dependencies and FFmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    # FFmpeg and codecs
    ffmpeg \
    # Fonts for Vietnamese support
    fonts-roboto \
    fonts-noto-cjk \
    fonts-dejavu-core \
    # Utilities
    curl \
    wget \
    dos2unix \
    # Clean up
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create app user (non-root)
RUN groupadd -r appuser && useradd -r -g appuser -m -d /home/appuser appuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/data /app/output /app/videos /app/audio /app/assets /app/.auth /app/logs \
    && chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser . /app/

# Fix line endings for scripts (Windows compatibility)
RUN dos2unix /app/docker/*.sh 2>/dev/null || true

# Make scripts executable
RUN chmod +x /app/docker/*.sh 2>/dev/null || true

# Download additional fonts if needed
RUN mkdir -p /app/assets/fonts /app/assets/icons /app/assets/logo

# Set environment variables
ENV PYTHONPATH="/app:$PYTHONPATH"
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Ho_Chi_Minh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import content_generator, layout_generator, video_assembly" || exit 1

# Switch to app user
USER appuser

# Default command (can be overridden)
ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["sleep", "infinity"]