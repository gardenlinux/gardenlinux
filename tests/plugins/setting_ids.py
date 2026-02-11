"""
Plugin to register custom pytest marker for Garden Linux setting IDs.
"""

import pytest


def pytest_configure(config: pytest.Config):
    """Register custom marker for Garden Linux setting IDs."""
    config.addinivalue_line(
        "markers",
        "setting_ids(ids): Mark tests with Garden Linux setting IDs for traceability",
    )
