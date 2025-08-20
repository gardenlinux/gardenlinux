import pytest
from typing import List

run_mutating_tests = False

def allow_system_modifications() -> bool:
    return run_mutating_tests


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--allow-system-modifications",
        action="store_true",
        help="Run tests that mutate system state. Disabling this is useful if running tests on a long-running system."
    )


def pytest_configure(config: pytest.Config):
    global run_mutating_tests
    run_mutating_tests = config.getoption("--allow-system-modifications")

    config.addinivalue_line("markers", "modify: this test mutates system state")


def pytest_collection_modifyitems(config: pytest.Config, items: List[pytest.Item]):
    for item in items:
        if item.get_closest_marker("modify") and not run_mutating_tests:
            item.add_marker(pytest.mark.skip(reason="skipping tests that mutate system state"))
