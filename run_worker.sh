#!/bin/bash
# Script to run the Celery worker for Reddit scraping

# Default values
CONCURRENCY=2
LOGLEVEL="info"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --concurrency=*)
      CONCURRENCY="${1#*=}"
      shift
      ;;
    --loglevel=*)
      LOGLEVEL="${1#*=}"
      shift
      ;;
    --help)
      echo "Usage: $0 [--concurrency=N] [--loglevel=LEVEL]"
      echo ""
      echo "Options:"
      echo "  --concurrency=N   Number of worker processes (default: 10)"
      echo "  --loglevel=LEVEL  Logging level: debug, info, warning, error, critical (default: info)"
      echo "  --help            Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Create necessary directories
mkdir -p local_storage/crawler

# Set PYTHONPATH to include the current directory
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run the Celery worker
echo "Starting Celery worker with concurrency $CONCURRENCY for queue $QUEUE"
celery -A app.workers.celery_app worker --concurrency=$CONCURRENCY  --loglevel=$LOGLEVEL
