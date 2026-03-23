FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Default port for Streamlit in Railway is often 8080
EXPOSE 8080

# Streamlit configuration
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Start command - Railway will map its dynamic port to 8080 if configured, 
# but we will use a fixed port to avoid the "$PORT" string error.
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
