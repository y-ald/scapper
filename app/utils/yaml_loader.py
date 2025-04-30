from datetime import datetime
from typing import Any, Dict, List

import yaml

from app.core.logger import logger


class YAMLLoader:
    """
    Utility class for loading and parsing YAML configuration files
    """

    @staticmethod
    def load_file(filepath: str) -> Dict[str, Any]:
        """
        Load a YAML file and return its contents as a dictionary

        Args:
            filepath (str): Path to the YAML file

        Returns:
            Dict[str, Any]: Dictionary containing the YAML file contents
        """
        try:
            with open(filepath, "r") as file:
                data = yaml.safe_load(file)
                logger.info(f"Successfully loaded YAML file: {filepath}")
                return data
        except Exception as e:
            logger.error(f"Error loading YAML file {filepath}: {e}")
            raise

    @staticmethod
    def get_reddit_users(data: Dict[str, Any]) -> List[str]:
        """
        Extract Reddit usernames from the YAML data

        Args:
            data (Dict[str, Any]): Dictionary containing the YAML data

        Returns:
            List[str]: List of Reddit usernames
        """
        users = data.get("reddit_users", [])
        logger.info(f"Found {len(users)} Reddit users in YAML data")
        return users

    @staticmethod
    def get_date_range(data: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract date range from the YAML data

        Args:
            data (Dict[str, Any]): Dictionary containing the YAML data

        Returns:
            Dict[str, str]: Dictionary with 'since' and 'until' dates
        """
        date_range = data.get("date_range", {})

        # Set default values if not provided
        if not date_range.get("since"):
            # Default to 30 days ago
            since = (
                datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                - datetime.timedelta(days=30)
            ).strftime("%Y-%m-%d")
            date_range["since"] = since

        if not date_range.get("until"):
            # Default to today
            until = datetime.now().strftime("%Y-%m-%d")
            date_range["until"] = until

        logger.info(f"Date range: {date_range['since']} to {date_range['until']}")
        return date_range

    @staticmethod
    def get_parameters(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract scraping parameters from the YAML data

        Args:
            data (Dict[str, Any]): Dictionary containing the YAML data

        Returns:
            Dict[str, Any]: Dictionary with scraping parameters
        """
        params = data.get("parameters", {})

        # Set default values if not provided
        if "min_posts_per_author" not in params:
            params["min_posts_per_author"] = 2

        if "min_date_span_days" not in params:
            params["min_date_span_days"] = 14

        if "delay_seconds" not in params:
            params["delay_seconds"] = 30

        logger.info(f"Scraping parameters: {params}")
        return params


# Create a singleton instance
yaml_loader = YAMLLoader()
