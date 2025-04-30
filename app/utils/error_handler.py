import functools
import random
import time

from app.core.logger import logger


class ScraperException(Exception):
    """Base exception for scraper errors"""


class RateLimitException(ScraperException):
    """Exception raised when rate limited"""


class AuthenticationException(ScraperException):
    """Exception raised when authentication fails"""


class NetworkException(ScraperException):
    """Exception raised for network errors"""


class ParsingException(ScraperException):
    """Exception raised when parsing fails"""


def retry_with_backoff(
    max_retries=3, base_delay=5, max_delay=60, exceptions=(Exception,)
):
    """
    Decorator for retrying functions with exponential backoff

    Args:
        max_retries (int): Maximum number of retries
        base_delay (int): Base delay in seconds
        max_delay (int): Maximum delay in seconds
        exceptions (tuple): Exceptions to catch and retry
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(
                            f"Max retries ({max_retries}) exceeded for {func.__name__}: {e}"
                        )
                        raise

                    # Calculate delay with exponential backoff and jitter
                    delay = min(
                        base_delay * (2 ** (retries - 1)) + random.uniform(0, 1),
                        max_delay,
                    )

                    # Log the retry
                    logger.warning(
                        f"Retry {retries}/{max_retries} for {func.__name__} after {delay:.2f}s: {e}"
                    )

                    # Wait before retrying
                    time.sleep(delay)

        return wrapper

    return decorator


def handle_http_error(status_code, response_text=None):
    """
    Handle HTTP error codes and raise appropriate exceptions

    Args:
        status_code (int): HTTP status code
        response_text (str, optional): Response text for additional context

    Raises:
        RateLimitException: For rate limiting (429)
        AuthenticationException: For authentication errors (401, 403)
        NetworkException: For server errors (5xx)
        ScraperException: For other errors
    """
    error_msg = f"HTTP Error {status_code}"
    if response_text:
        error_msg += f": {response_text[:200]}..."

    if status_code == 429:
        raise RateLimitException(f"Rate limited: {error_msg}")
    elif status_code in (401, 403):
        raise AuthenticationException(f"Authentication failed: {error_msg}")
    elif 500 <= status_code < 600:
        raise NetworkException(f"Server error: {error_msg}")
    else:
        raise ScraperException(error_msg)
