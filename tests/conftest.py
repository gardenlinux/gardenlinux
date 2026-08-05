import os

import pytest

plugin_dir = os.path.join(os.path.dirname(__file__), "plugins")
pytest_plugins = [
    f"plugins.{f[:-3]}"
    for f in os.listdir(plugin_dir)
    if f.endswith(".py") and not f.startswith("_")
]

handler_dir = os.path.join(os.path.dirname(__file__), "handlers")
pytest_plugins += [
    f"handlers.{f[:-3]}"
    for f in os.listdir(handler_dir)
    if f.endswith(".py") and not f.startswith("_")
]

for plugin in pytest_plugins:
    pytest.register_assert_rewrite(plugin)


def pytest_assertrepr_compare(op, left, right):
    if op == "in" and isinstance(right, str) and len(right) > 200:
        return [
            f"Assertion failed: '{left}' not found in comparison string.",
            f"Comparison string (truncated): {right[:200]}...",
        ]
    return None


@pytest.fixture(scope="session", autouse=True)
def include_metadata_in_junit_xml_session(include_metadata_in_junit_xml):
    """Session-scoped fixture that uses pytest-metadata's include_metadata_in_junit_xml fixture."""
    return include_metadata_in_junit_xml
