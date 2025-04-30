from abc import ABC, abstractmethod
from typing import Any, Dict


class StorageInterface(ABC):
    """
    Abstract interface for storage implementations
    """

    @abstractmethod
    def upload_json(self, data: Dict[str, Any], path: str) -> str:
        """
        Upload JSON data to storage

        Args:
            data (Dict[str, Any]): JSON-serializable data
            path (str): Path within the storage

        Returns:
            str: Path or identifier of the stored data
        """

    @abstractmethod
    def upload_file(self, filepath: str, object_name: str) -> str:
        """
        Upload a file to storage

        Args:
            filepath (str): Source file path
            object_name (str): Destination path within storage

        Returns:
            str: Path or identifier of the stored file
        """


class StorageFactory:
    """
    Factory class for creating storage instances
    """

    @staticmethod
    def get_storage(storage_type: str = "local"):
        """
        Get a storage instance based on the specified type

        Args:
            storage_type (str): Type of storage ('local' or 'minio')

        Returns:
            StorageInterface: Storage implementation
        """
        if storage_type == "local":
            from app.storage.local_storage import local_storage

            return local_storage
        elif storage_type == "minio":
            from app.storage.minio_client import MinIOStorage

            return MinIOStorage()
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")
