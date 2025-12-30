# Dockerfile for Microservice 5 - ML Service
FROM python:3.11-slim

# Install curl for health checks and libgomp for LightGBM
RUN apt-get update && apt-get install -y curl libgomp1 && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code (including models directory)
COPY . .

# Expose the API port
EXPOSE 8001

# Launch the API
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8001"]
