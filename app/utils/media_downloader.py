import hashlib
import os
import uuid
from urllib.parse import urlparse
from urllib.request import getproxies

import requests

from app.core.logger import logger
from app.utils.throttling import wait_random_delay
from app.utils.user_agents import user_agent_manager


class MediaDownloader:
    def __init__(self, download_dir="downloads"):
        """Initialize the media downloader with a target directory"""
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        logger.info(f"Media will be downloaded to {os.path.abspath(download_dir)}")

    def _get_file_extension(self, url, content_type=None):
        """Determine file extension from URL or content type"""
        # Try to get extension from URL
        path = urlparse(url).path
        ext = os.path.splitext(path)[1]

        if ext:
            return ext.lower()

        # If no extension in URL, try to determine from content type
        if content_type:
            if "image/jpeg" in content_type or "image/jpg" in content_type:
                return ".jpg"
            elif "image/png" in content_type:
                return ".png"
            elif "image/gif" in content_type:
                return ".gif"
            elif "video/mp4" in content_type:
                return ".mp4"
            elif "video/webm" in content_type:
                return ".webm"
            elif "audio/mpeg" in content_type:
                return ".mp3"

        # Default extension if we can't determine
        return ".bin"

    def download_media(self, url):
        """
        Download media from URL and return local path

        Args:
            url (str): URL of the media to download

        Returns:
            str: Local path where media was saved
        """
        try:
            # Add a small delay before downloading
            wait_random_delay(base=5)  # Shorter delay for media downloads

            user_agent = user_agent_manager.get_random_user_agent()

            # Setup headers and proxies
            headers = {"User-Agent": user_agent}

            # Make request
            response = requests.get(
                url, headers=headers, proxies=getproxies(), stream=True, timeout=30
            )
            response.raise_for_status()

            # Generate a unique filename
            url_hash = hashlib.md5(url.encode()).hexdigest()[:10]
            file_ext = self._get_file_extension(
                url, response.headers.get("Content-Type")
            )
            filename = f"{url_hash}_{uuid.uuid4().hex[:6]}{file_ext}"
            filepath = os.path.join(self.download_dir, filename)

            # Save the file
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            logger.info(f"Downloaded {url} to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            return None

    def download_multiple(self, urls):
        """
        Download multiple media files and return list of local paths

        Args:
            urls (list): List of URLs to download

        Returns:
            list: List of local paths where media was saved (None for failed downloads)
        """
        local_paths = []
        for url in urls:
            local_path = self.download_media(url)
            local_paths.append(local_path)

        # Filter out None values (failed downloads)
        return [path for path in local_paths if path]


# Singleton instance
media_downloader = MediaDownloader()
