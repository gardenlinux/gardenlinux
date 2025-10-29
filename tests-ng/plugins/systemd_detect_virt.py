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
_HYPERVISOR_HINTS: dict[Hypervisor, list[str]] = {
    Hypervisor.microsoft: ["microsoft"],
    Hypervisor.amazon: ["amazon", "aws"],
    Hypervisor.google: ["google"],
    Hypervisor.oracle: ["oracle"],
    Hypervisor.vmware: ["vmware"],
}


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

        name: str = result.stdout.strip()
        detected: Hypervisor = (
            Hypervisor[name] if name in Hypervisor.__members__ else Hypervisor.none
        )

        # double check the hypervisor by using the system's metadata
        # in case where q QEMU environment falsely reports as Azure or AWS
        sys_vendor: str = ""
        product_name: str = ""

        for path in ("/sys/class/dmi/id/sys_vendor", "/sys/class/dmi/id/product_name"):
            try:
                with open(path, "r") as f:
                    data: str = f.read().strip().lower()
                    if "sys_vendor" in path:
                        sys_vendor = data
                    else:
                        product_name = data
            except FileNotFoundError:
                pass

        # Hints that we are not on a real hypervisor.

        # if a known hypervisor was detected by systemd, but none of its
        # expected DMI entries are actually present, it's likely
        # that this is a virtualized test environment (e.g. Azure image under QEMU).
        expected_signatures = _HYPERVISOR_HINTS.get(detected)
        if expected_signatures and not any(
            any(keyword in field for keyword in expected_signatures)
            for field in (sys_vendor, product_name)
        ):
            # no real hypervisor, fall back to qemu
            return Hypervisor.qemu

        return detected
    except Exception:
        return Hypervisor.none


@pytest.fixture
def systemd_detect_virt() -> Hypervisor:
    return detect_hypervisor()


def pytest_configure(config: pytest.Config):
    config.addinivalue_line(
        "markers",
        "hypervisor(*names): run test only on given hypervisors, "
        "e.g. @pytest.mark.hypervisor('microsoft', 'google')",
    )
    config.stash[_HYPERVISOR_KEY] = detect_hypervisor()


def pytest_collection_modifyitems(config, items: list[pytest.Item]):
    """Evaluate skip/only markers once fixtures are available"""
    hypervisor = config.stash.get(_HYPERVISOR_KEY, Hypervisor.none)

    for item in items:
        marker = item.get_closest_marker("hypervisor")
        if not marker:
            continue

        allowed = [h.lower() for h in marker.args]
        if hypervisor.name.lower() not in allowed:
            item.add_marker(
                pytest.mark.skip(
                    reason=(
                        f"Skipped. Test marked to only run on {', '.join(allowed)} (current: {hypervisor.name})"
                    )
                )
            )
