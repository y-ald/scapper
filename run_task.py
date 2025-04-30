#!/usr/bin/env python3
"""
Script to run Celery tasks for Reddit scraping
"""

import argparse
import os
import sys
from datetime import datetime

from app.utils.yaml_loader import yaml_loader
from app.workers.tasks import crawl_reddit_author, crawl_reddit_users_from_yaml


def run_single_task(author_id, since, until, storage_type):
    """
    Run a single task to crawl a Reddit author

    Args:
        author_id (str): Reddit username
        since (str): Start date in YYYY-MM-DD format
        until (str): End date in YYYY-MM-DD format
        storage_type (str): Storage type ('local' or 'minio')
    """
    print(f"Scheduling task to crawl Reddit author: {author_id}")
    print(f"Date range: {since} to {until}")
    print(f"Storage type: {storage_type}")

    task = crawl_reddit_author.delay(author_id, since, until, storage_type)
    print(f"Task scheduled with ID: {task.id}")

    return task.id


def run_yaml_task(yaml_path, storage_type):
    """
    Run a task to crawl Reddit users from a YAML file

    Args:
        yaml_path (str): Path to the YAML configuration file
        storage_type (str): Storage type ('local' or 'minio')
    """
    if not os.path.exists(yaml_path):
        print(f"Error: YAML file '{yaml_path}' not found")
        return 1

    print(f"Scheduling task to crawl Reddit users from YAML: {yaml_path}")
    print(f"Storage type: {storage_type}")

    # Load the YAML file to display information
    config_data = yaml_loader.load_file(yaml_path)
    reddit_users = yaml_loader.get_reddit_users(config_data)
    date_range = yaml_loader.get_date_range(config_data)
    crawler_processing_timestamp = datetime.now().timestamp()
    
    print(f"Found {len(reddit_users)} Reddit users in YAML file")
    print(f"Date range: {date_range.get('since')} to {date_range.get('until')}")

    # Schedule the task
    task = crawl_reddit_users_from_yaml.delay(yaml_path, storage_type, crawler_processing_timestamp)
    print(f"Task scheduled with ID: {task.id}")

    return task.id


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run Celery tasks for Reddit scraping")
    parser.add_argument("--author", help="Reddit username to crawl")
    parser.add_argument(
        "--since", default="2023-01-01", help="Start date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "--until", default="2025-12-31", help="End date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "--yaml", default="users.yaml", help="Path to YAML configuration file"
    )
    parser.add_argument(
        "--storage",
        default="local",
        choices=["local", "minio"],
        help="Storage type (local or minio)",
    )
    args = parser.parse_args()

    # Set PYTHONPATH to include the current directory
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

    # Create necessary directories
    os.makedirs("local_storage/metadata", exist_ok=True)
    os.makedirs("local_storage/media", exist_ok=True)
    os.makedirs("downloads", exist_ok=True)
    os.makedirs("results", exist_ok=True)

    if args.author:
        # Run a single task for a specific author
        run_single_task(args.author, args.since, args.until, args.storage)
    else:
        # Run a task for all users in the YAML file
        run_yaml_task(args.yaml, args.storage)

    print(
        "\nTask(s) scheduled. Check Flower dashboard for status: http://localhost:5555"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
