import os
from typing import List

import pytest


def get_current_arch() -> str:
    """Get the current architecture as a normalized string."""
    machine = os.uname().machine
    arch_map = {
        "x86_64": "amd64",
        "aarch64": "arm64",
    }
    return arch_map.get(machine, machine)


def pytest_configure(config: pytest.Config):
    config.addinivalue_line(
        "markers",
        "arch(architecture): mark test to run only on specific architecture(s). "
        "Supported: amd64, arm64",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: List[pytest.Item]):
    """Skip tests that are not for the current architecture."""
    current_arch = get_current_arch()

    for item in items:
        arch_marker = item.get_closest_marker("arch")
        if arch_marker:
            marker_arg = arch_marker.args[0] if arch_marker.args else None
            allowed_archs = (
                [marker_arg] if isinstance(marker_arg, str) else list(marker_arg or [])
            )

            if allowed_archs and current_arch not in allowed_archs:
                skip_msg = f"test requires architecture {allowed_archs}, current: {current_arch}"
                item.add_marker(pytest.mark.skip(skip_msg))
