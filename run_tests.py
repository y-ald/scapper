#!/usr/bin/env python3
"""
Script to run all tests
"""

import argparse
import os
import sys
import unittest


def discover_and_run_tests(test_dir="tests", pattern="test_*.py", verbosity=2):
    """
    Discover and run tests in the specified directory

    Args:
        test_dir (str): Directory containing tests
        pattern (str): Pattern to match test files
        verbosity (int): Verbosity level (1-3)
    """
    # Ensure the test directory exists
    if not os.path.exists(test_dir):
        print(f"Test directory '{test_dir}' not found.")
        return 1

    # Discover tests
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern=pattern)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)

    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1


def run_specific_test(test_path):
    """
    Run a specific test file

    Args:
        test_path (str): Path to the test file
    """
    if not os.path.exists(test_path):
        print(f"Test file '{test_path}' not found.")
        return 1

    # Add the directory to the path
    test_dir = os.path.dirname(test_path)
    if test_dir:
        sys.path.insert(0, test_dir)

    # Run the test
    return os.system(f"python {test_path}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run tests for the Reddit scraper")
    parser.add_argument("--test", help="Run a specific test file")
    parser.add_argument("--dir", default="tests", help="Directory containing tests")
    parser.add_argument(
        "--pattern", default="test_*.py", help="Pattern to match test files"
    )
    parser.add_argument(
        "--verbosity",
        type=int,
        default=2,
        choices=[1, 2, 3],
        help="Verbosity level (1-3)",
    )
    args = parser.parse_args()

    if args.test:
        return run_specific_test(args.test)
    else:
        return discover_and_run_tests(args.dir, args.pattern, args.verbosity)


if __name__ == "__main__":
    sys.exit(main())
