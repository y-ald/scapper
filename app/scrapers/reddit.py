from datetime import datetime
from typing import List, Optional

import praw
import requests

from app.config import settings
from app.core.logger import logger
from app.models import Author, Post
from app.utils.error_handler import (
    RateLimitException,
    ScraperException,
    retry_with_backoff,
)
from app.utils.throttling import wait_random_delay
from app.utils.user_agents import user_agent_manager

from .base import BaseScraper


class RedditScraper(BaseScraper):
    """
    Reddit scraper using PRAW (Python Reddit API Wrapper)
    """

    REDDIT_API_BASE = "https://www.reddit.com"

    def __init__(self, client_id=None, client_secret=None, user_agent=None):
        """
        Initialize the Reddit scraper

        Args:
            client_id (str, optional): Reddit API client ID
            client_secret (str, optional): Reddit API client secret
            user_agent (str, optional): User agent for Reddit API
        """
        super().__init__()

        # Use provided credentials, config settings, or defaults
        self.client_id = client_id or settings.REDDIT_CLIENT_ID or "YOUR_CLIENT_ID"
        self.client_secret = (
            client_secret or settings.REDDIT_CLIENT_SECRET or "YOUR_CLIENT_SECRET"
        )
        self.user_agent = user_agent or user_agent_manager.get_random_user_agent()

        # Initialize PRAW for authenticated API access if credentials are provided
        if (
            self.client_id != "YOUR_CLIENT_ID"
            and self.client_secret != "YOUR_CLIENT_SECRET"
        ):
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent,
            )
            self.authenticated = True
            logger.info("Initialized Reddit scraper with API credentials")
        else:
            # Fall back to read-only mode without authentication
            self.reddit = praw.Reddit(
                user_agent=self.user_agent,
                check_for_updates=False,
                comment_kind="t1",
                message_kind="t4",
                redditor_kind="t2",
                submission_kind="t3",
                subreddit_kind="t5",
                trophy_kind="t6",
                oauth_url="https://oauth.reddit.com",
                reddit_url="https://www.reddit.com",
                short_url="https://redd.it",
                ratelimit_seconds=5,
                timeout=16,
            )
            self.authenticated = False
            logger.info(
                "Initialized Reddit scraper in read-only mode (no API credentials)"
            )

    @retry_with_backoff(
        max_retries=3,
        exceptions=(ScraperException, RateLimitException, requests.RequestException),
    )
    def fetch_author(self, author_id: str) -> Author:
        """
        Fetch author information from Reddit

        Args:
            author_id (str): Reddit username

        Returns:
            Author: Author object with Reddit user information
        """
        logger.info(f"Fetching Reddit author: {author_id}")
        wait_random_delay()

        try:
            # Get the Redditor object
            redditor = self.reddit.redditor(author_id)

            # Force loading of attributes by accessing a property
            # This will trigger an API call
            name = redditor.name

            # Extract creation date
            created_utc = redditor.created_utc
            created_at = (
                datetime.fromtimestamp(created_utc).isoformat() if created_utc else None
            )

            # Try to get follower count (may not be available)
            followers_count = None
            try:
                # This is only available for some users and requires authentication
                if hasattr(redditor, "followers") and self.authenticated:
                    followers_count = len(redditor.followers)
            except Exception:
                pass

            # Create Author object
            author = Author(
                id=author_id,
                name=name,
                created_at=created_at,
                followers_count=followers_count,
                following_count=None,  # Reddit doesn't provide this directly
            )

            logger.info(f"Successfully fetched Reddit author: {author_id}")
            return author

        except praw.exceptions.PRAWException as e:
            logger.error(f"PRAW error fetching Reddit user {author_id}: {e}")
            raise ScraperException(f"Failed to fetch Reddit user: {e}")
        except Exception as e:
            logger.error(f"Error fetching Reddit user {author_id}: {e}")
            raise ScraperException(f"Failed to fetch Reddit user: {e}")

    @retry_with_backoff(
        max_retries=3,
        exceptions=(ScraperException, RateLimitException, requests.RequestException),
    )
    def fetch_posts(self, author_id: str, since: str, until: str) -> List[Post]:
        """
        Fetch posts by a Reddit user within a date range

        Args:
            author_id (str): Reddit username
            since (str): Start date in YYYY-MM-DD format
            until (str): End date in YYYY-MM-DD format

        Returns:
            List[Post]: List of Post objects
        """
        logger.info(f"Fetching Reddit posts for {author_id} from {since} to {until}")

        # Parse date strings to datetime objects
        since_date = self._parse_date(since)
        until_date = self._parse_date(until)

        try:
            # Get the Redditor object
            redditor = self.reddit.redditor(author_id)
            logger.info(f"Redditor object for {redditor} fetched successfully")
            # Get submissions (posts)
            submissions = (
                redditor.submissions.new()
            )  # top(time_filter="all")  # Adjust limit as needed
            print(f"Submissions: {submissions}")
            posts = []
            n = 0
            for submission in submissions:
                if n > 2:
                    break
                n += 1
                logger.info(f"Processing submission: {submission.id}")
                logger.info(f"Submission title: {submission.title}")
                logger.info(f"Submission URL: {submission.url}")
                logger.info(f"Submission created at: {submission.created_utc}")
                # Add delay between processing posts to avoid rate limiting
                wait_random_delay(base=5)  # Shorter delay for this

                # Check if post is within date range
                created_utc = submission.created_utc
                post_date = datetime.fromtimestamp(created_utc)
                logger.info(f"Post date: {post_date}")
                logger.info(f"Since date: {since_date}, Until date: {until_date}")
                # Check if the post date is within the specified range
                if post_date < since_date or post_date > until_date:
                    continue

                # Process the submission
                post = self._process_submission(submission, author_id)
                if post:
                    posts.append(post)

            logger.info(f"Found {len(posts)} posts for {author_id}")
            return posts

        except praw.exceptions.PRAWException as e:
            logger.error(f"PRAW error fetching posts for {author_id}: {e}")
            raise ScraperException(f"Failed to fetch posts: {e}")
        except Exception as e:
            logger.error(f"Error fetching posts for {author_id}: {e}")
            raise ScraperException(f"Failed to fetch posts: {e}")

    def _process_submission(self, submission, author_id: str) -> Optional[Post]:
        """
        Process a submission from Reddit API

        Args:
            submission: PRAW Submission object
            author_id (str): Reddit username

        Returns:
            Optional[Post]: Post object or None if processing fails
        """
        try:
            # Extract text content
            text = submission.selftext or submission.title

            # Convert timestamp
            created_utc = submission.created_utc
            timestamp = (
                datetime.fromtimestamp(created_utc).isoformat() if created_utc else None
            )

            # Extract media URLs
            media_urls = self._extract_media_urls(submission)

            # Download media
            media_local_paths = self._download_media(media_urls) if media_urls else []

            # Create Post object
            post = Post(
                author_id=author_id,
                text=text,
                timestamp=timestamp,
                likes=submission.score,
                reposts=0,  # Reddit doesn't have a direct "repost" concept
                comments=submission.num_comments,
                media_urls=media_urls,
                media_local_paths=media_local_paths,
            )

            return post

        except Exception as e:
            logger.error(
                f"Error processing submission {getattr(submission, 'id', 'unknown')}: {e}"
            )
            return None

    def _extract_media_urls(self, submission) -> List[str]:
        """
        Extract media URLs from a Reddit submission

        Args:
            submission: PRAW Submission object

        Returns:
            List[str]: List of media URLs
        """
        media_urls = []

        try:
            # Check for direct image/video URL
            url = submission.url
            if url and self._is_media_url(url):
                media_urls.append(url)

            # Check for gallery
            if hasattr(submission, "is_gallery") and submission.is_gallery:
                if hasattr(submission, "media_metadata"):
                    for item_id in submission.media_metadata:
                        item = submission.media_metadata[item_id]
                        if "s" in item and "u" in item["s"]:
                            media_urls.append(item["s"]["u"])

            # Check for media
            if submission.media:
                if "reddit_video" in submission.media:
                    video_url = submission.media["reddit_video"].get("fallback_url")
                    if video_url:
                        media_urls.append(video_url)

            # Check for preview images
            if hasattr(submission, "preview") and "images" in submission.preview:
                for image in submission.preview["images"]:
                    if "source" in image and "url" in image["source"]:
                        media_urls.append(image["source"]["url"])

        except Exception as e:
            logger.error(f"Error extracting media URLs: {e}")

        return media_urls

    def _is_media_url(self, url: str) -> bool:
        """
        Check if a URL is likely to be a media URL

        Args:
            url (str): URL to check

        Returns:
            bool: True if URL is likely a media URL
        """
        media_extensions = [".jpg", ".jpeg", ".png", ".gif", ".mp4", ".webm", ".webp"]
        return any(url.lower().endswith(ext) for ext in media_extensions)
