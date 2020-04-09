"""Run all tests."""
import pytest

pytest.main(
    [
        # "-x",   # stop on first failure
        "--log-auto-indent=true",
        "--log-cli-level=INFO",
        "--log-level=INFO",
        "--showlocals",
        "integration/",
    ]
)
