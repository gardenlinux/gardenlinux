import os
import pytest

plugin_dir = os.path.join(os.path.dirname(__file__), "plugins")
pytest_plugins = [
    f"plugins.{f[:-3]}"
    for f in os.listdir(plugin_dir)
    if f.endswith(".py") and not f.startswith("_")
]


@pytest.fixture(scope="session", autouse=True)
def include_metadata_in_junit_xml_session(include_metadata_in_junit_xml):
    """Session-scoped fixture that uses pytest-metadata's include_metadata_in_junit_xml fixture."""
    return include_metadata_in_junit_xml
