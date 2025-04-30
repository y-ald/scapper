import json
import os
from typing import Any, Dict

from app.core.logger import logger
from app.storage.storage_interface import StorageInterface


class LocalStorage(StorageInterface):
    """
    Local file system storage implementation
    """

    def __init__(self, base_dir: str = "local_storage"):
        """
        Initialize the local storage with a base directory

        Args:
            base_dir (str): Base directory for local storage
        """
        self.base_dir = base_dir

        # Create base directory if it doesn't exist
        os.makedirs(self.base_dir, exist_ok=True)

        # Create subdirectories for metadata and media
        self.metadata_dir = os.path.join(self.base_dir, "metadata")
        self.media_dir = os.path.join(self.base_dir, "media")

        os.makedirs(self.metadata_dir, exist_ok=True)
        os.makedirs(self.media_dir, exist_ok=True)

        logger.info(f"Initialized local storage at {os.path.abspath(self.base_dir)}")

    def upload_json(self, data: Dict[str, Any], path: str) -> str:
        """
        Save JSON data to a local file

        Args:
            data (Dict[str, Any]): JSON-serializable data
            path (str): Relative path within the storage

        Returns:
            str: Full path to the saved file
        """
        # Ensure the directory exists
        full_path = os.path.join(self.metadata_dir, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Write the JSON file
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved JSON data to {full_path}")
            return full_path
        except Exception as e:
            logger.error(f"Error saving JSON data to {full_path}: {e}")
            raise

    def upload_file(self, filepath: str, object_name: str) -> str:
        """
        Copy a file to local storage

        Args:
            filepath (str): Source file path
            object_name (str): Destination path within storage

        Returns:
            str: Full path to the saved file
        """
        # Ensure the directory exists
        full_path = os.path.join(self.media_dir, object_name)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Copy the file
        try:
            import shutil

            shutil.copy2(filepath, full_path)

            logger.info(f"Copied file from {filepath} to {full_path}")
            return full_path
        except Exception as e:
            logger.error(f"Error copying file from {filepath} to {full_path}: {e}")
            raise

    def list_files(self, prefix: str = "") -> list:
        """
        List files in the storage with an optional prefix

        Args:
            prefix (str): Optional prefix to filter files

        Returns:
            list: List of file paths
        """
        files = []

        # List files in metadata directory
        metadata_path = os.path.join(self.metadata_dir, prefix)
        if os.path.exists(metadata_path):
            for root, _, filenames in os.walk(metadata_path):
                for filename in filenames:
                    rel_path = os.path.relpath(
                        os.path.join(root, filename), self.metadata_dir
                    )
                    files.append(rel_path)

        # List files in media directory
        media_path = os.path.join(self.media_dir, prefix)
        if os.path.exists(media_path):
            for root, _, filenames in os.walk(media_path):
                for filename in filenames:
                    rel_path = os.path.relpath(
                        os.path.join(root, filename), self.media_dir
                    )
                    files.append(rel_path)

        return files

    def read_json(self, path: str) -> Dict[str, Any]:
        """
        Read JSON data from a local file

        Args:
            path (str): Relative path within the storage

        Returns:
            Dict[str, Any]: JSON data
        """
        full_path = os.path.join(self.metadata_dir, path)

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            logger.info(f"Read JSON data from {full_path}")
            return data
        except Exception as e:
            logger.error(f"Error reading JSON data from {full_path}: {e}")
            raise


# Create a singleton instance
local_storage = LocalStorage()
