import json
import os
import random

from fake_useragent import UserAgent

from app.core.logger import logger


class UserAgentManager:
    def __init__(self, user_agents_file=None):
        self.user_agents = []
        self.ua_generator = UserAgent()

        # Try to load from file if provided
        if user_agents_file and os.path.exists(user_agents_file):
            try:
                with open(user_agents_file, "r") as f:
                    self.user_agents = json.load(f)
                logger.info(f"Loaded {len(self.user_agents)} user agents from file")
            except Exception as e:
                logger.error(f"Error loading user agents from file: {e}")
                self._populate_default_agents()
        else:
            self._populate_default_agents()

    def _populate_default_agents(self):
        # Populate with some common user agents as fallback
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        ]
        logger.info("Using default user agents")

    def get_random_user_agent(self):
        """Get a random user agent from the list or generate a new one"""
        try:
            # Try to generate a random user agent first
            return self.ua_generator.random
        except Exception as e:
            logger.warning(
                f"Failed to generate user agent: {e}, using from list instead"
            )
            # Fall back to the predefined list
            return random.choice(self.user_agents)


# Singleton instance
user_agent_manager = UserAgentManager()
