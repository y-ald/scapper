#!/usr/bin/env python3
"""
Simple test script to verify the scrapers are working correctly
"""

import os
import sys
from datetime import datetime, timedelta

# Add the scrapers directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "scrapers"))

from scrapers.reddit import RedditScraper


def test_reddit_scraper():
    """Test the Reddit scraper"""
    print("\n=== Testing Reddit Scraper ===")

    # Get Reddit API credentials from environment variables
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("⚠️ Reddit API credentials not found in environment variables.")
        print("  Running in read-only mode with limited functionality.")

    # Create a Reddit scraper
    reddit_scraper = RedditScraper(client_id=client_id, client_secret=client_secret)

    # Test fetch_author
    print("\nTesting fetch_author...")
    try:
        author = reddit_scraper.fetch_author("Drakoniid")
        print(f"✅ Successfully fetched author: {author.name}")
        print(f"  ID: {author.id}")
        print(f"  Created at: {author.created_at}")
        print(f"  Followers: {author.followers_count}")
    except Exception as e:
        print(f"❌ Error fetching author: {e}")

    # Test fetch_posts
    print("\nTesting fetch_posts...")
    try:
        # Get posts from the last 7 days
        until_date = datetime.now().strftime("%Y-%m-%d")
        since_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        posts = reddit_scraper.fetch_posts("Drakoniid", since_date, until_date)
        print(f"✅ Successfully fetched {len(posts)} posts")

        if posts:
            print(f"  First post: {posts[0].text[:50]}...")
            print(f"  Date: {posts[0].timestamp}")
            print(f"  Likes: {posts[0].likes}, Comments: {posts[0].comments}")
    except Exception as e:
        print(f"❌ Error fetching posts: {e}")


def main():
    """Run the tests"""
    print("=== Reddit and LinkedIn Scraper Tests ===")
    print("This script will test the basic functionality of the scrapers.")

    # Run the tests
    test_reddit_scraper()

    print("\n=== Tests Completed ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
