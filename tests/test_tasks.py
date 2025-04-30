#!/usr/bin/env python3
"""
Test script for Celery tasks
"""

import os
import sys
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.logger import logger
from app.models import Author, Post
from app.workers.tasks import crawl_reddit_author, crawl_reddit_users_from_yaml


class TestCeleryTasks(unittest.TestCase):
    """Test the Celery tasks"""

    def setUp(self):
        """Set up the test environment"""
        # Mock data
        self.author_id = "test_user"
        self.since = "2023-01-01"
        self.until = "2025-12-31"

        # Mock author
        self.mock_author = Author(
            id=self.author_id,
            name="Test User",
            created_at=datetime.now().isoformat(),
            followers_count=100,
            following_count=50,
        )

        # Mock posts
        self.mock_posts = [
            Post(
                author_id=self.author_id,
                text="Test post 1",
                timestamp=datetime.now().isoformat(),
                likes=10,
                reposts=5,
                comments=3,
                media_urls=["http://example.com/image1.jpg"],
                media_local_paths=["/tmp/image1.jpg"],
            ),
            Post(
                author_id=self.author_id,
                text="Test post 2",
                timestamp=datetime.now().isoformat(),
                likes=20,
                reposts=10,
                comments=6,
                media_urls=["http://example.com/image2.jpg"],
                media_local_paths=["/tmp/image2.jpg"],
            ),
        ]

    @patch("app.workers.tasks.RedditScraper")
    @patch("app.workers.tasks.StorageFactory.get_storage")
    def test_crawl_reddit_author(self, mock_storage_factory, mock_reddit_scraper):
        """Test the crawl_reddit_author task"""
        # Set up mocks
        mock_scraper_instance = mock_reddit_scraper.return_value
        mock_scraper_instance.fetch_author.return_value = self.mock_author
        mock_scraper_instance.fetch_posts.return_value = self.mock_posts

        mock_storage = mock_storage_factory.return_value

        # Call the task
        result = crawl_reddit_author(self.author_id, self.since, self.until, "local")

        # Check that the scraper was called correctly
        mock_scraper_instance.fetch_author.assert_called_once_with(self.author_id)
        mock_scraper_instance.fetch_posts.assert_called_once_with(
            self.author_id, self.since, self.until
        )

        # Check that the storage was called correctly
        self.assertEqual(mock_storage.upload_json.call_count, 3)  # 1 author + 2 posts
        self.assertEqual(mock_storage.upload_file.call_count, 2)  # 2 media files

        # Check the result
        self.assertEqual(result["author_id"], self.author_id)
        self.assertEqual(result["posts_count"], 2)
        self.assertEqual(result["media_count"], 2)

def main():
    """Run the tests"""
    unittest.main()


if __name__ == "__main__":
    main()
