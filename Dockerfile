FROM python:3.11-slim

LABEL maintainer="Hans AI <admin@hans-ai.com>"
LABEL description="Mem0 Memory Server for Hans AI Dashboard"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    MEM0_HOST=0.0.0.0 \
    MEM0_PORT=8002

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY mem0_server.py /app/
COPY app/ /app/app/

# Create non-root user
RUN useradd -m -u 1000 memuser && \
    chown -R memuser:memuser /app
USER memuser

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Run application
CMD ["uvicorn", "mem0_server:app", "--host", "0.0.0.0", "--port", "8002"]
