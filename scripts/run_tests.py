#!/usr/bin/env python3
"""
Test runner script for different environments.

Usage:
    python scripts/run_tests.py [mode]

Modes:
    unit      - Run only unit tests (work everywhere)
    mock      - Run unit + mock tests (work everywhere)
    local     - Run unit + mock + local tests (local environment)
    container - Run unit + mock + container tests (container environment)
    all       - Run all tests (including integration tests with real services)
    ci        - Run tests for CI/CD pipeline (unit + mock only)
"""

import os
import subprocess
import sys


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")

    result = subprocess.run(cmd, capture_output=False)

    if result.returncode != 0:
        print(f"\n❌ {description} failed with exit code {result.returncode}")
        return False
    else:
        print(f"\n✅ {description} completed successfully")
        return True


def get_test_mode():
    """Get test mode from command line or environment."""
    if len(sys.argv) > 1:
        return sys.argv[1]

    # Default based on environment
    if os.getenv("DOCKER_CONTAINER"):
        return "container"
    elif os.getenv("CI"):
        return "ci"
    else:
        return "local"


def get_test_commands(mode):
    """Get test commands for different modes."""
    base_cmd = ["poetry", "run", "pytest"]

    commands = {
        "unit": [base_cmd + ["tests/unit/", "-m", "unit", "-v"]],
        "mock": [base_cmd + ["tests/unit/", "tests/api/", "-m", "unit or mock", "-v"]],
        "local": [
            base_cmd
            + ["tests/unit/", "tests/api/", "-m", "unit or mock or local", "-v"]
        ],
        "container": [
            base_cmd
            + ["tests/unit/", "tests/api/", "-m", "unit or mock or container", "-v"]
        ],
        "all": [base_cmd + ["tests/", "-v", "--tb=short"]],
        "ci": [
            base_cmd
            + ["tests/unit/", "tests/api/", "-m", "unit or mock", "-v", "--tb=short"]
        ],
    }

    return commands.get(mode, commands["local"])


def main():
    """Main function."""
    mode = get_test_mode()

    print(f"🧪 Running tests in {mode.upper()} mode")
    print(
        f"Environment: {'Docker Container' if os.getenv('DOCKER_CONTAINER') else 'Local'}"
    )
    print(f"CI: {'Yes' if os.getenv('CI') else 'No'}")

    commands = get_test_commands(mode)

    all_passed = True

    for i, cmd in enumerate(commands, 1):
        description = f"Test Suite {i}/{len(commands)} ({mode} mode)"
        if not run_command(cmd, description):
            all_passed = False

    if all_passed:
        print(f"\n🎉 All tests passed in {mode} mode!")
        sys.exit(0)
    else:
        print(f"\n💥 Some tests failed in {mode} mode!")
        sys.exit(1)


if __name__ == "__main__":
    main()
