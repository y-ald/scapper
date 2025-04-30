import json
import os
from tempfile import NamedTemporaryFile
from typing import Any, Dict

from minio import Minio

from app.config import settings
from app.core.logger import logger
from app.storage.storage_interface import StorageInterface


class MinIOStorage(StorageInterface):
    """
    MinIO storage implementation
    """

    def __init__(self):
        """
        Initialize the MinIO client with settings from config
        """
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False,
        )

        # Create bucket if it doesn't exist
        if not self.client.bucket_exists(settings.MINIO_BUCKET):
            self.client.make_bucket(settings.MINIO_BUCKET)
            logger.info(f"Created MinIO bucket: {settings.MINIO_BUCKET}")
        else:
            logger.info(f"Using existing MinIO bucket: {settings.MINIO_BUCKET}")

    def upload_json(self, data: Dict[str, Any], path: str) -> str:
        """
        Upload JSON data to MinIO

        Args:
            data (Dict[str, Any]): JSON-serializable data
            path (str): Path within the bucket

        Returns:
            str: Path of the uploaded object
        """
        try:
            # Create a temporary file
            with NamedTemporaryFile(delete=False, mode="w", suffix=".json") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                temp_path = f.name

            # Upload the file to MinIO
            self.client.fput_object(settings.MINIO_BUCKET, path, temp_path)

            # Clean up the temporary file
            os.unlink(temp_path)

            logger.info(f"Uploaded JSON data to MinIO: {path}")
            return path

        except Exception as e:
            logger.error(f"Error uploading JSON to MinIO at {path}: {e}")
            raise

    def upload_file(self, filepath: str, object_name: str) -> str:
        """
        Upload a file to MinIO

        Args:
            filepath (str): Source file path
            object_name (str): Destination path within the bucket

        Returns:
            str: Path of the uploaded object
        """
        try:
            self.client.fput_object(settings.MINIO_BUCKET, object_name, filepath)

            logger.info(f"Uploaded file from {filepath} to MinIO: {object_name}")
            return object_name

        except Exception as e:
            logger.error(f"Error uploading file to MinIO at {object_name}: {e}")
            raise

    def list_objects(self, prefix: str = "") -> list:
        """
        List objects in the bucket with an optional prefix

        Args:
            prefix (str): Optional prefix to filter objects

        Returns:
            list: List of object names
        """
        try:
            objects = self.client.list_objects(
                settings.MINIO_BUCKET, prefix=prefix, recursive=True
            )
            return [obj.object_name for obj in objects]

        except Exception as e:
            logger.error(f"Error listing objects in MinIO with prefix {prefix}: {e}")
            raise
