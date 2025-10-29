import subprocess
from enum import Enum

import pytest
from plugins.shell import ShellRunner
from pytest import StashKey


class Hypervisor(Enum):
    """
    ids according to https://www.freedesktop.org/software/systemd/man/latest/systemd-detect-virt.html
    """

    none = 0
    qemu = 1
    kvm = 2
    amazon = 3
    zvm = 4
    vmware = 5
    microsoft = 6
    oracle = 7
    powervm = 8
    xen = 9
    bochs = 10
    uml = 11
    parallels = 12
    hbyve = 13
    qnx = 14
    acrn = 15
    apple = 16
    sre = 17
    google = 18


_HYPERVISOR_KEY: StashKey[Hypervisor] = StashKey[Hypervisor]()


def detect_hypervisor() -> Hypervisor:
    try:
        result = subprocess.run(
            ["systemd-detect-virt", "-v"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return Hypervisor.none

        name = result.stdout.strip()
        return Hypervisor[name] if name in Hypervisor.__members__ else Hypervisor.none
    except Exception:
        return Hypervisor.none


@pytest.fixture
def systemd_detect_virt() -> Hypervisor:
    return detect_hypervisor()


def pytest_configure(config: pytest.Config):
    config.addinivalue_line(
        "markers",
        "skip_on_hypervisor(*names): skip test when running under given hypervisors, "
        "e.g. @pytest.mark.skip_on_hypervisor('qemu', 'amazon')",
    )
    config.addinivalue_line(
        "markers",
        "only_on_hypervisor(*names): run test only on given hypervisors, "
        "e.g. @pytest.mark.only_on_hypervisor('microsoft', 'google')",
    )
    config.stash[_HYPERVISOR_KEY] = detect_hypervisor()


def pytest_collection_modifyitems(config, items: list[pytest.Item]):
    """Evaluate skip/only markers once fixtures are available"""
    hypervisor = config.stash.get(_HYPERVISOR_KEY, Hypervisor.none)

    for item in items:
        skip_marker = item.get_closest_marker("skip_on_hypervisor")
        only_marker = item.get_closest_marker("only_on_hypervisor")

        if skip_marker:
            to_skip = [h.lower() for h in skip_marker.args]
            if hypervisor.name.lower() in to_skip:
                item.add_marker(
                    pytest.mark.skip(reason=f"Skipped on hypervisor: {hypervisor.name}")
                )

        if only_marker:
            allowed = [h.lower() for h in only_marker.args]
            if hypervisor.name.lower() not in allowed:
                item.add_marker(
                    pytest.mark.skip(
                        reason=(
                            f"Skipped. Test marked to only run on {', '.join(allowed)} (current: {hypervisor.name})"
                        )
                    )
                )
