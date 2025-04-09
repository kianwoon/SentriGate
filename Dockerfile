FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including supervisord
RUN apt-get update && apt-get install -y --no-install-recommends \
    supervisor \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy requirements
COPY pyproject.toml .

# Install dependencies
RUN uv pip install --system .

# Install additional dependencies required for monitoring
RUN uv pip install --system psutil requests

# Copy application code
COPY . .

# Copy supervisord configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create non-root user
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Run supervisord as entry point
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]