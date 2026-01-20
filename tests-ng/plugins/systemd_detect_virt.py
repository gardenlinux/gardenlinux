import subprocess
from enum import Enum

import pytest
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
    Hypervisor.google: ["google", "gdch"],
    Hypervisor.oracle: ["oracle"],
    Hypervisor.vmware: ["vmware"],
}


def get_hypervisor_claim() -> Hypervisor:
    """
    Uses systemd-detect-virt to detect the hypervisor OS image claims to be running on.

    This claim can deviate from reality when running cloud images in virtualized test
    environments.
    """
    try:
        result = subprocess.run(
            ["systemd-detect-virt", "-v"],
            capture_output=True,
            text=True,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        print("[systemd-detect-virt] Failed to run `systemd-detect-virt`.")
        return Hypervisor.none

    if result.returncode != 0:
        return Hypervisor.none

    name = result.stdout.strip()
    if not name:
        return Hypervisor.none

    return Hypervisor.__members__.get(name, Hypervisor.none)


def get_hypervisor_hints_from_dmi() -> Hypervisor:
    """
    Search for hints within the system's DMI parameters to detect
    the kind of hypervisor it is running on (if any).

    Usually indicated by brand names or keywords somewhere in sys_vendor, product_name
    or bios_vendor tables.
    """
    dmi_entries: list[str] = []

    for path in (
        "/sys/class/dmi/id/sys_vendor",
        "/sys/class/dmi/id/product_name",
        "/sys/class/dmi/id/bios_vendor",
    ):
        try:
            with open(path, "r") as fb:
                dmi_entries.append(fb.read().strip().lower())
        except FileNotFoundError:
            continue
        except OSError:
            continue

    if not dmi_entries:
        return Hypervisor.none

    # Hints for generic virtualization (QEMU/KVM)
    for entry in dmi_entries:
        if any(hint in entry for hint in ("qemu", "kvm", "bochs", "edk ii")):
            return Hypervisor.qemu

    # Cloud / vendor-specific branding
    for hypervisor, hints in _HYPERVISOR_HINTS.items():
        for entry in dmi_entries:
            for hint in hints:
                if hint in entry:
                    return hypervisor

    return Hypervisor.none


def detect_hypervisor() -> Hypervisor:
    """
    Determine the effective hypervisor for test expectations
    by reconciling multiple detection mechanisms.

    We distinguish between the hypervisor the OS image claims it is using
    (via systemd-detect-virt) and the hypervisor suggested by DMI metadata.
    DMI-based QEMU or generic virtualization are treated as authoritative.

    If the OS image claims a cloud hypervisor (e.g. AWS, Azure, GCP)
    but no corresponding DMI branding is present, we assume the image
    is running in a virtualized test environment which is emulating
    parts of a hypervisor's behaviour.

    This distinction is necessary because certain tests rely on the presence of
    real cloud services (e.g. provider-specific NTP or metadata endpoints), which
    are not available in emulated test environments.
    """
    claim = get_hypervisor_claim()
    dmi = get_hypervisor_hints_from_dmi()

    # 1. If DMI strongly suggests QEMU, trust it over the claims of the image
    if dmi == Hypervisor.qemu:
        return Hypervisor.qemu

    # 2. If both mechanisms agree, trust the result
    if dmi == claim:
        return claim

    # 3. If systemd claims a cloud hypervisor but DMI is inconclusive,
    #    assume a virtualized test environment
    if claim in _HYPERVISOR_HINTS and dmi == Hypervisor.none:
        return Hypervisor.qemu

    # 4. Otherwise, prefer the image's claim if it is plausible
    if claim != Hypervisor.none:
        return claim

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
        reason = marker.kwargs.get("reason")

        if hypervisor.name.lower() not in allowed:
            skip_reason = (
                reason
                or f"Skipped. Test marked to only run on {', '.join(allowed)} (current: {hypervisor.name})"
            )
            item.add_marker(pytest.mark.skip(reason=skip_reason))
