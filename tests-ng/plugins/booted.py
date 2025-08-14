import pytest
from typing import Any, List

system_booted = False


def is_system_booted() -> bool:
    return system_booted


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--system-booted",
        action="store_true",
        help="Set if the system under test was booted instead of running in a chroot or container. This will enable kernel, systemd, and other system level tests."
    )


def pytest_configure(config: pytest.Config):
    global system_booted
    system_booted = config.getoption("--system-booted")

    config.addinivalue_line("markers", "booted: mark test to run only on a booted target, i.e. not in a container or chroot")


def pytest_collection_modifyitems(config: pytest.Config, items: List[pytest.Item]):
    for item in items:
        if item.get_closest_marker("booted") and not system_booted:
            item.add_marker(pytest.mark.skip(reason="not running on a booted system"))
