FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Create directories for local storage
RUN mkdir -p /app/local_storage/metadata /app/local_storage/media /app/downloads

# Set environment variables
ENV PYTHONPATH=/app

# Run Celery worker
CMD ["celery", "-A", "app.workers.celery_app", "worker", "--concurrency=$CONCURRENCY","--loglevel=info"]
