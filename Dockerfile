FROM python:3.10-slim

WORKDIR /app

# Install system compilation packages safely
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Optimize layer caching for requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Configuration environments
ENV FLASK_ENV=testing
# FIX: Points PYTHONPATH directly to /app so 'from services.x' or 'from src.services.x' resolve safely
ENV PYTHONPATH=/app:/app/src

# FIX: Copy the entire src directory tree cleanly to preserve all internal paths
COPY src/ /app/src/

# Copy your configuration contracts
COPY specmatic_contract.yaml /app/
COPY specmatic_resiliency.yaml /app/

EXPOSE 5000

# Execute the application
CMD ["python", "src/app.py"]
