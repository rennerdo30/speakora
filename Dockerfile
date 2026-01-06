# Base image - supports both CPU and GPU (NVIDIA CUDA)
# For GPU: Use nvidia/cuda:12.1-runtime-ubuntu22.04 as base
# For CPU: Use python:3.10-slim
ARG BASE_IMAGE=python:3.10-slim
FROM ${BASE_IMAGE}

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV OUTPUT_DIR=/app/output
ENV SEAMLESS_DEVICE=auto

# Create necessary directories
RUN mkdir -p /app/input /app/output/translated /app/output/metadata /app/output/logs /app/output/backups /app/config

# Expose API port
EXPOSE 5000

# Entry point will be handled by docker-compose or overridden
CMD ["python", "tool/main.py", "--help"]
