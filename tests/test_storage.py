#!/usr/bin/env python3
"""
Test script for storage implementations
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.storage.storage_interface import StorageFactory
from app.core.logger import logger
from app.storage.local_storage import LocalStorage
from app.storage.minio_client import MinIOStorage


class TestLocalStorage(unittest.TestCase):
    """Test the local storage implementation"""

    def setUp(self):
        """Set up the test environment"""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.storage = LocalStorage(base_dir=self.temp_dir)

        # Test data
        self.test_data = {
            "id": "test_user",
            "name": "Test User",
            "created_at": datetime.now().isoformat(),
            "followers_count": 100,
            "following_count": 50,
        }

        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        self.temp_file.write(b"Test content")
        self.temp_file.close()

    def tearDown(self):
        """Clean up after tests"""
        import shutil

        shutil.rmtree(self.temp_dir)
        os.unlink(self.temp_file.name)

    def test_upload_json(self):
        """Test uploading JSON data"""
        path = "test/user.json"
        result = self.storage.upload_json(self.test_data, path)

        # Check that the file exists
        full_path = os.path.join(self.temp_dir, "metadata", path)
        self.assertTrue(os.path.exists(full_path))

        # Check that the content is correct
        with open(full_path, "r") as f:
            data = json.load(f)

        self.assertEqual(data["id"], self.test_data["id"])
        self.assertEqual(data["name"], self.test_data["name"])

    def test_upload_file(self):
        """Test uploading a file"""
        object_name = "test/file.txt"
        result = self.storage.upload_file(self.temp_file.name, object_name)

        # Check that the file exists
        full_path = os.path.join(self.temp_dir, "media", object_name)
        self.assertTrue(os.path.exists(full_path))

        # Check that the content is correct
        with open(full_path, "r") as f:
            content = f.read()

        self.assertEqual(content, "Test content")

    def test_list_files(self):
        """Test listing files"""
        # Upload some files
        self.storage.upload_json(self.test_data, "test/user1.json")
        self.storage.upload_json(self.test_data, "test/user2.json")
        self.storage.upload_file(self.temp_file.name, "test/file1.txt")
        self.storage.upload_file(self.temp_file.name, "test/file2.txt")

        # List files
        files = self.storage.list_files()

        # Check that all files are listed
        self.assertEqual(len(files), 4)

        # List files with prefix
        files = self.storage.list_files("test")

        # Check that all files with the prefix are listed
        self.assertEqual(len(files), 4)


class TestStorageFactory(unittest.TestCase):
    """Test the storage factory"""

    def test_get_local_storage(self):
        """Test getting local storage"""
        storage = StorageFactory.get_storage("local")
        self.assertIsInstance(storage, LocalStorage)

    def test_get_minio_storage(self):
        """Test getting MinIO storage"""
        storage = StorageFactory.get_storage("minio")
        self.assertIsInstance(storage, MinIOStorage)

    def test_invalid_storage_type(self):
        """Test getting an invalid storage type"""
        with self.assertRaises(ValueError):
            StorageFactory.get_storage("invalid")


def main():
    """Run the tests"""
    unittest.main()


if __name__ == "__main__":
    main()
