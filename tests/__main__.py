"""Run all tests."""
import pytest

pytest.main(
    [
        "--log-auto-indent=true",
        "--log-cli-level=INFO",
        "--log-level=INFO",
        "--showlocals",
        "integration/",
    ]
)
