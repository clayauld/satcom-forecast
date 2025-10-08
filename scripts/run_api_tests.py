#!/usr/bin/env python3
"""
Test runner script for API migration tests.

This script provides an easy way to run different types of tests for the
Weather.gov API migration implementation.
"""

import argparse
import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest


def run_unit_tests():
    """Run unit tests."""
    print("Running unit tests...")
    return pytest.main([
        "tests/test_api_client.py",
        "tests/test_api_data_processor.py", 
        "tests/test_api_formatter.py",
        "-v",
        "--tb=short"
    ])


def run_integration_tests():
    """Run integration tests with real API endpoints."""
    print("Running integration tests...")
    return pytest.main([
        "tests/test_api_integration.py",
        "-v",
        "--tb=short",
        "-m", "integration"
    ])


def run_compatibility_tests():
    """Run compatibility tests."""
    print("Running compatibility tests...")
    return pytest.main([
        "tests/test_api_compatibility.py",
        "-v",
        "--tb=short",
        "-m", "compatibility"
    ])


def run_performance_tests():
    """Run performance tests."""
    print("Running performance tests...")
    return pytest.main([
        "tests/test_api_integration.py",
        "tests/test_api_compatibility.py",
        "-v",
        "--tb=short",
        "-m", "slow"
    ])


def run_all_tests():
    """Run all tests."""
    print("Running all tests...")
    return pytest.main([
        "tests/test_api_*.py",
        "-v",
        "--tb=short"
    ])


def run_specific_test(test_file):
    """Run a specific test file."""
    print(f"Running {test_file}...")
    return pytest.main([
        f"tests/{test_file}",
        "-v",
        "--tb=short"
    ])


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run API migration tests")
    parser.add_argument(
        "test_type",
        choices=["unit", "integration", "compatibility", "performance", "all", "specific"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--file",
        help="Specific test file to run (only for 'specific' type)"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage reporting"
    )
    parser.add_argument(
        "--html-report",
        action="store_true",
        help="Generate HTML coverage report"
    )
    
    args = parser.parse_args()
    
    # Build pytest command
    pytest_args = []
    
    if args.coverage:
        pytest_args.extend(["--cov=custom_components.satcom_forecast", "--cov-report=term"])
        
        if args.html_report:
            pytest_args.extend(["--cov-report=html:htmlcov"])
    
    # Run appropriate tests
    if args.test_type == "unit":
        exit_code = run_unit_tests()
    elif args.test_type == "integration":
        exit_code = run_integration_tests()
    elif args.test_type == "compatibility":
        exit_code = run_compatibility_tests()
    elif args.test_type == "performance":
        exit_code = run_performance_tests()
    elif args.test_type == "all":
        exit_code = run_all_tests()
    elif args.test_type == "specific":
        if not args.file:
            print("Error: --file required for 'specific' test type")
            sys.exit(1)
        exit_code = run_specific_test(args.file)
    else:
        print(f"Unknown test type: {args.test_type}")
        sys.exit(1)
    
    # Add coverage args if specified
    if args.coverage and pytest_args:
        # Re-run with coverage
        if args.test_type == "unit":
            exit_code = pytest.main(["tests/test_api_client.py", "tests/test_api_data_processor.py", "tests/test_api_formatter.py"] + pytest_args)
        elif args.test_type == "integration":
            exit_code = pytest.main(["tests/test_api_integration.py", "-m", "integration"] + pytest_args)
        elif args.test_type == "compatibility":
            exit_code = pytest.main(["tests/test_api_compatibility.py", "-m", "compatibility"] + pytest_args)
        elif args.test_type == "all":
            exit_code = pytest.main(["tests/test_api_*.py"] + pytest_args)
    
    if exit_code == 0:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed!")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()