# 1. Use an official lightweight Python base image
FROM python:3.10-slim

# 2. Set the working directory inside the container space
WORKDIR /app

# 3. Install necessary system-level C++ build compilers (Required for Scikit-Learn)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy dependency requirements file first to take advantage of Docker layer caching
COPY requirements.txt .

# 5. Upgrade pip and install all Python dependencies cleanly
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Inject the environment variable to force the app into Specmatic testing mode
ENV FLASK_ENV=testing

# 7. Copy individual files from your root directory
COPY app.py .
COPY specmatic_contract.yaml .
COPY specmatic_resiliency.yaml .
COPY indian_finance_ml_dataset_balanced_final.csv .

# 8. Copy individual application subfolders from your root directory
COPY contracts/ ./contracts/
COPY models/ ./models/
COPY utils/ ./utils/
COPY templates/ ./templates/
COPY static/ ./static/

# 9. Expose your Flask server's internal network communication port
EXPOSE 5000

# 10. Start your Flask application execution server
CMD ["python", "app.py"]
