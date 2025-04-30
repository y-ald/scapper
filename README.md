# 🛠️ Complete Crawling Solution - Reddit

A scalable, fault-tolerant web crawling application to extract data from Reddit, storing results in MinIO (both JSON metadata and media files) and locally, using Object-Oriented Python, Celery, RabbitMQ, MinIO, and Docker Compose.

## Project Overview

### Key Features

- **Scalable Architecture**: Uses Celery and RabbitMQ for distributed task processing
- **Fault Tolerance**: Implements retry mechanisms with exponential backoff
- **Data Storage**: Stores data in MinIO (S3-compatible object storage)
- **User-Agent Rotation**: Randomizes user agents to mimic different browsers
- **Rate Limiting**: Enforces delays between requests to respect website limits
- **Media Downloading**: Downloads and stores media files from posts

## Technical Architecture

```
+-------------+       +-----------+       +-----------+       +-------------+
| Scheduler   | ----> | RabbitMQ  | ----> | Celery    | ----> | Scrapers    |
| (cron/API)  |       |           |       | Workers   |       | Reddit
+-------------+       +-----------+       +-----------+
                                                                    |
        +------------------+                     +----------------------------+
        | MinIO (bronze)   | <------------------ | JSON Metadata + Media Files |
        +------------------+                     +----------------------------+
```

## Docker Stack

The application is fully containerized using Docker Compose with the following services:

- **RabbitMQ**: Message broker for Celery tasks
- **Celery Workers**: 10 workers for Reddit scraping
- **MinIO**: Object storage for JSON metadata and media files
- **Flower**: Dashboard for monitoring Celery tasks

## Project Structure

```
app/
├── config.py                # Configuration settings from environment variables
├── models.py                # Pydantic models for data structures
├── main.py                  # Main script for local execution
├── core/
│   ├── logger.py            # Logging configuration
├── scrapers/
│   ├── base.py              # Base scraper class with common functionality
│   ├── reddit.py            # Reddit-specific scraper implementation
├── workers/
│   ├── celery_app.py        # Celery application configuration
│   └── tasks.py             # Celery tasks for scraping
├── storage/
│   └── minio_client.py      # MinIO client for object storage
├── utils/
│   ├── error_handler.py     # Error handling and retry mechanisms
│   ├── media_downloader.py  # Media downloading functionality
│   ├── throttling.py        # Rate limiting implementation
│   └── user_agents.py       # User-Agent rotation
tests/
├── test_scrapers.py         # Tests for scrapers
├── test_storage.py          # Tests for storage functionality
└── test_tasks.py            # Tests for Celery tasks
.env.template                # Template for environment variables
docker-compose.yml           # Docker Compose configuration
Dockerfile                   # Docker image definition
requirements.txt             # Python dependencies
```

## Data Extraction

### Authors

The following data is extracted for Reddit authors:

- `id`: Unique identifier (username)
- `name`: Display name
- `created_at`: Account creation date
- `followers_count`: Number of followers (if available)
- `following_count`: Number of accounts followed (if available)

### Posts

The following data is extracted for Reddit posts:

- `text`: Post content
- `timestamp`: Post creation time
- `likes`: Number of upvotes
- `reposts`: Number of reposts (not directly available on Reddit)
- `comments`: Number of comments
- `media_urls`: URLs of media attachments
- `media_local_paths`: Local paths where media files are stored

### Storage Structure

- Metadata is stored as JSON under `bronze/metadata/reddit/<author_id>.json`
- Media files are stored under `bronze/media/reddit/<author_id>/<timestamp>.<ext>`

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.10+
- Reddit API credentials (optional, enhances functionality)

### Environment Setup

1. Copy the `.env.template` and `.env_docker.template`file to `.env` and `.env_docker`:

   ```bash
   cp .env.template .env
   cp .env_docker.template .env_docker
   ```

2. Edit the `.env` and `env_docker` file to add your credentials:

   ```
   # Reddit API credentials (optional but recommended)
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret

   # MinIO credentials
   MINIO_ACCESS_KEY=your_minio_key
   MINIO_SECRET_KEY=your_minio_secret
   ```

### Running

Edit users.yaml to specify the Reddit users you want to scrape.

1. Create virtual Environment and Start docker
   Start services:

   ```bash
   docker compose up rabbitmq minio flower -d
   ```

   This will start:

   - RabbitMQ on port 5672 (management UI on 15672)
   - MinIO on port 9000 (console on 9001)
   - Celery workers (10 workers for Reddit)
   - Flower dashboard on port 5555

   Create virtual environment

   ```
   python -m venv env
   ```

2. Install dependencies:

   ```bash
   env/bin/python -m pip install -r requirements.txt
   ```

3. Create necessary directories (if using local as storage and not minio):

   ```bash
   mkdir -p local_storage/
   ```

4. Run the Celery worker:
   With Local Script

   ```bash
   # Start a worker with default settings
   ./run_worker.sh

   # Start a worker with custom concurrency
   ./run_worker.sh --concurrency=5

   # Start a worker with debug logging
   ./run_worker.sh --loglevel=debug
   ```

   With Docker

   ```bash
   docker compose up reddit_worker -d
   ```

5. Launch tasks:

   ```bash
   # Schedule tasks for all users in the YAML file
   ./run_task.py

   # Schedule a task for a specific user
   ./run_task.py --author=spez

   # Schedule a task with custom date range
   ./run_task.py --author=spez --since=2023-06-01 --until=2023-12-31

   # Schedule tasks with MinIO storage
   ./run_task.py --storage=minio
   ```

### Running Tests

Run all tests:

```bash
./run_tests.py
```

Run a specific test file:

```bash
./run_tests.py --test=tests/test_storage.py
```

## Monitoring

- **RabbitMQ Management**: http://localhost:15672 (guest/guest)
- **Flower Dashboard**: http://localhost:5555
- **MinIO Console**: http://localhost:9000 (credentials from .env)

## Scraping & Proxy Management

- **Fixed 30s delay** between requests with random jitter
- **Proxy and User-Agent rotation** for avoiding detection
- **Error handling** with exponential backoff for retries

## Data Coverage

For each author, the system attempts to retrieve at least 2 posts over a minimum 14-day span. This ensures a representative sample of the author's activity.

## Testing

Run the tests:

```bash
pytest tests/
```

Individual test files can be run directly:

```bash
python tests/test_scrapers.py
```

## Security Considerations

- Credentials are stored in `.env` files (not committed to version control)
- Proxies are rotated to avoid IP bans
- User agents are randomized to mimic different browsers
- Rate limiting respects website terms of service

## Future Enhancements

- **FastAPI Integration**: Add a REST API for triggering scraping jobs
- **S3 Support**: Add support for AWS S3 as an alternative to MinIO
- **Advanced Analytics**: Integrate with data processing pipelines
- **Captcha Handling**: Add support for solving captchas
- **Stealth Mode**: Implement browser-based scraping with Playwright for dynamic content(LinkedIn)

# Known Limitations and Areas for Improvement

#### Scraper Component

- **LinkedIn Scraping**: Scraping for LinkedIn has not been implemented. An initial attempt was made, but the solution did not work as expected and was eventually abandoned.
- **Reddit Scraping**: The Reddit scraper currently does not retrieve the number of followers or followings for users, which limits user profile insights.
- **Proxy Handling**: The project currently relies on `getproxies` from `Url`. For better control and reliability, a reverse proxy such as [Caddy](https://caddyserver.com/) should be installed. This would allow better management of proxy rotation at our level.

#### Data Processing Component

- **Incomplete Processing Pipeline**: Unfortunately, we were not able to achieve a fully functional data processing pipeline. We encountered a key issue in the **bronze layer** due to Snowflake's inability to read **multiline JSON files**, which we discovered too late in development.
- **Pipeline Placeholder**: We have included a preliminary version of the processing code, which is intended to be industrialized later into a proper pipeline, potentially orchestrated via Snowflake tasks or another orchestration tool.
- **Archiving Strategy**: One improvement would be to implement an archiving function that moves already-processed files from the bronze layer to an archive folder. This would ensure that each pipeline run only reads new files, avoiding unnecessary filtering and improving efficiency.
- **Silver Layer Modeling**: The modeling in the silver layer can also be improved to avoid overwriting all data on each delta run. Implementing incremental logic would be a better long-term approach.
