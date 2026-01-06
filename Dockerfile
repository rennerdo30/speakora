FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV OUTPUT_DIR=/app/output
ENV SEAMLESS_DEVICE=cpu

# Expose API port
EXPOSE 5000

# Entry point will be handled by docker-compose or overridden
CMD ["python", "tool/main.py", "--help"]
