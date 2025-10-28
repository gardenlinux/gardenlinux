from typing import List

import pytest


def pytest_configure(config: pytest.Config):
    config.addinivalue_line(
        "markers",
        "security_id(id=None): Map a test to a security id.",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: List[pytest.Item]):
    for item in items:
        for marker in item.iter_markers(name="security_id"):
            # To map the required tests for our compliance, we define a custom marker.
            # We add this marker to the user_properties field so it appears in any generated report.
            # https://docs.pytest.org/en/4.6.x/reference.html#item
            security_id = marker.args[0]
            item.user_properties.append(("security_id", security_id))
