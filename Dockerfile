FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PORT=5000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libpq-dev \
        libzbar0 \
        curl \
        postgresql-client \
        redis-tools \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Create directories for uploads and logs with proper permissions
RUN mkdir -p static/uploads/food logs \
    && chmod -R 755 static/uploads \
    && chmod -R 755 logs

# Create non-root user
RUN groupadd -r nutricoach \
    && useradd -r -g nutricoach -s /bin/bash nutricoach \
    && chown -R nutricoach:nutricoach /app

# Switch to non-root user
USER nutricoach

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:5000/api/healthz || exit 1

# Run the application with proper signal handling
CMD ["./entrypoint.sh"]