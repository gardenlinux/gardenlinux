import os

import pathlib
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


@pytest.fixture(scope="session", autouse=True)
def include_metadata_in_junit_xml_session(include_metadata_in_junit_xml):
    """Session-scoped fixture that uses pytest-metadata's include_metadata_in_junit_xml fixture."""
    return include_metadata_in_junit_xml

### <test>
ALLOWED = ["test_iscsi.py"]

def pytest_ignore_collect(collection_path):
    print(f'{collection_path.name=}')
    if collection_path.is_file() and collection_path.name in ALLOWED:
        return False

    return True
### </test>
