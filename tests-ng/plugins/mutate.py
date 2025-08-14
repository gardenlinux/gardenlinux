import pytest
from typing import List

skip_mutating_tests = False


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--skip-mutating-tests",
        action="store_true",
        help="Skip tests that mutate system state. Useful if running tests on a long-running system."
    )


def pytest_configure(config: pytest.Config):
    global skip_mutating_tests
    skip_mutating_tests = config.getoption("--skip-mutating-tests")

    config.addinivalue_line("markers", "mutating_test: this test mutates system state")


def pytest_collection_modifyitems(config: pytest.Config, items: List[pytest.Item]):
    for item in items:
        if item.get_closest_marker("mutating_test") and skip_mutating_tests:
            item.add_marker(pytest.mark.skip(reason="skipping tests that mutate system state"))
