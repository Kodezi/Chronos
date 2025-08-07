# Kodezi Chronos Production Dockerfile
FROM python:3.9-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /build

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production image
FROM python:3.9-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    git \
    docker.io \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -s /bin/bash chronos

# Copy Python packages from builder
COPY --from=builder /root/.local /home/chronos/.local

# Create necessary directories
RUN mkdir -p /app /var/chronos /var/repositories /models \
    && chown -R chronos:chronos /app /var/chronos /var/repositories /models

# Switch to app directory
WORKDIR /app

# Copy application code
COPY --chown=chronos:chronos . .

# Set Python path
ENV PATH=/home/chronos/.local/bin:$PATH
ENV PYTHONPATH=/app:$PYTHONPATH

# Switch to non-root user
USER chronos

# Expose ports
EXPOSE 5000 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Default command
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "5000"]