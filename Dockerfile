FROM python:3.11-slim

# Set working directory
WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
# Run with gunicorn (production)
CMD gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 2 --timeout 120 app:app
