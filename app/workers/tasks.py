import os

from datetime import datetime

from app.core.logger import logger
from app.scrapers.reddit import RedditScraper
from app.storage.storage_interface import StorageFactory
from app.utils.yaml_loader import yaml_loader
from app.workers.celery_app import celery_app


@celery_app.task(name="tasks.crawl_reddit_author")
def crawl_reddit_author(
    author_id: str, since: str, until: str, crawler_processing_timestamp: datetime, storage_type: str = "minio"
):
    """
    Celery task to crawl a Reddit author and store the data

    Args:
        author_id (str): Reddit username
        since (str): Start date in YYYY-MM-DD format
        until (str): End date in YYYY-MM-DD format
        storage_type (str): Storage type ('local' or 'minio')
    """
    logger.info(f"Starting Celery task to crawl Reddit author: {author_id}")

    # Create scraper and storage
    scraper = RedditScraper()
    storage = StorageFactory.get_storage(storage_type)

    try:
        # Fetch and store author data
        author = scraper.fetch_author(author_id)
        author_path = f"bronze/crawler/metadata/user_profil/{crawler_processing_timestamp}/reddit/{author_id}.json"
        storage.upload_json(author.model_dump(), author_path)
        logger.info(f"Stored author data for {author_id} in {storage_type} storage")

        # Fetch and store posts
        posts = scraper.fetch_posts(author_id, since, until)
        logger.info(f"Found {len(posts)} posts for {author_id}")

        for post in posts:
            # Store post metadata
            post_timestamp = post.timestamp.replace(":", "-")
            post_path = f"bronze/crawler/metadata/user_post/{crawler_processing_timestamp}/reddit/{author_id}/{post_timestamp}.json"
            storage.upload_json(post.model_dump(), post_path)

            # Store media files
            for i, media_path in enumerate(post.media_local_paths):
                if media_path and os.path.exists(media_path):
                    ext = os.path.splitext(media_path)[1]
                    media_object_name = (
                        f"bronze/crawler/media/reddit/{author_id}/{post_timestamp}_{i}{ext}"
                    )
                    storage.upload_file(media_path, media_object_name)

        return {
            "author_id": author_id,
            "posts_count": len(posts),
            "media_count": sum(len(post.media_local_paths) for post in posts),
        }

    except Exception as e:
        logger.error(f"Error in crawl_reddit_author task for {author_id}: {e}")
        raise


@celery_app.task(name="tasks.crawl_reddit_users_from_yaml")
def crawl_reddit_users_from_yaml(yaml_path: str, crawler_processing_timestamp: datetime,storage_type: str = "minio"):
    """
    Celery task to crawl multiple Reddit users from a YAML configuration

    Args:
        yaml_path (str): Path to the YAML configuration file
        storage_type (str): Storage type ('local' or 'minio')
    """
    logger.info(f"Starting Celery task to crawl Reddit users from YAML: {yaml_path}")

    try:
        # Load configuration from YAML
        config_data = yaml_loader.load_file(yaml_path)
        reddit_users = yaml_loader.get_reddit_users(config_data)
        date_range = yaml_loader.get_date_range(config_data)

        since_date = date_range.get("since")
        until_date = date_range.get("until")

        logger.info(f"Scheduling tasks for {len(reddit_users)} Reddit users")

        # Schedule individual tasks for each user
        results = []
        for user in reddit_users:
            task = crawl_reddit_author.delay(user, since_date, until_date, storage_type, crawler_processing_timestamp)
            results.append({"user": user, "task_id": task.id})

        return results

    except Exception as e:
        logger.error(f"Error in crawl_reddit_users_from_yaml task: {e}")
        raise   
