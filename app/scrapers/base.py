from abc import ABC, abstractmethod
from typing import List
from datetime import datetime
import requests
from app.models import Author, Post
from app.core.logger import logger
from app.utils.user_agents import user_agent_manager
from app.utils.media_downloader import media_downloader
from app.utils.error_handler import handle_http_error, ScraperException
import urllib.request


class BaseScraper(ABC):
    """Base class for all scrapers"""

    def __init__(self):
        """Initialize the scraper with common attributes"""
        self.session = requests.Session()

    def _get_headers(self):
        """Get headers with a random user agent"""
        return {"User-Agent": user_agent_manager.get_random_user_agent()}

    def _make_request(
        self, url, method="GET", params=None, data=None, json=None, headers=None
    ):
        """
        Make an HTTP request with retry logic and error handling

        Args:
            url (str): URL to request
            method (str): HTTP method (GET, POST, etc.)
            params (dict, optional): Query parameters
            data (dict, optional): Form data
            json (dict, optional): JSON data
            headers (dict, optional): HTTP headers

        Returns:
            requests.Response: Response object
        """
        # Combine default headers with any provided headers
        request_headers = self._get_headers()
        if headers:
            request_headers.update(headers)

        proxies = urllib.request.getproxies()
        # Make the request
        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json,
                headers=request_headers,
                proxies=proxies,
                timeout=30,
            )

            # Check for HTTP errors
            if response.status_code != 200:
                handle_http_error(response.status_code, response.text)

            return response

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            raise ScraperException(f"Request failed: {e}")

    def _parse_date(self, date_str):
        """
        Parse a date string in YYYY-MM-DD format to datetime

        Args:
            date_str (str): Date string in YYYY-MM-DD format

        Returns:
            datetime: Parsed datetime object
        """
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            logger.error(f"Invalid date format: {date_str}, expected YYYY-MM-DD")
            raise ValueError(f"Invalid date format: {date_str}, expected YYYY-MM-DD")

    def _download_media(self, urls):
        """
        Download media from URLs

        Args:
            urls (list): List of media URLs

        Returns:
            list: List of local file paths
        """
        return media_downloader.download_multiple(urls)

    @abstractmethod
    def fetch_author(self, author_id: str) -> Author:
        """
        Fetch author information

        Args:
            author_id (str): ID of the author

        Returns:
            Author: Author object
        """

    @abstractmethod
    def fetch_posts(self, author_id: str, since: str, until: str) -> List[Post]:
        """
        Fetch posts by an author within a date range

        Args:
            author_id (str): ID of the author
            since (str): Start date in YYYY-MM-DD format
            until (str): End date in YYYY-MM-DD format

        Returns:
            List[Post]: List of Post objects
        """
