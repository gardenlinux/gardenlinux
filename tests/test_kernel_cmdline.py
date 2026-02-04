"""Test kernel command line console configuration."""

from typing import List

import pytest
from plugins.kernel_cmdline import kernel_cmdline


@pytest.mark.testcov(
    [
        "GL-TESTCOV-ali-config-kernel-cmdline-console",
        "GL-TESTCOV-aws-config-kernel-cmdline-console",
        "GL-TESTCOV-azure-config-kernel-cmdline-console",
        "GL-TESTCOV-gcp-config-kernel-cmdline-console",
        # "GL-TESTCOV-gdch-config-kernel-cmdline-console",
        "GL-TESTCOV-kvm-config-kernel-cmdline-console",
        "GL-TESTCOV-lima-config-kernel-cmdline-console",
        "GL-TESTCOV-metal-config-kernel-cmdline-console",
        "GL-TESTCOV-openstack-config-kernel-cmdline-console",
        "GL-TESTCOV-vmware-config-kernel-cmdline-console",
    ]
)
@pytest.mark.feature(
    "ali or aws or azure or gcp or kvm or lima or metal or openstack or vmware"
)
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_console_configuration_in_cmdline(kernel_cmdline: List[str]):
    """Verify console parameters are present in the running kernel command line."""
    assert (
        "console=tty0" in kernel_cmdline
    ), "Virtual console (tty0) not found in kernel cmdline"
    assert (
        "console=ttyS0" in kernel_cmdline
    ), "Serial console (ttyS0) not found in kernel cmdline"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-lima-config-kernel-cmdline-console",
        "GL-TESTCOV-metal-config-kernel-cmdline-console",
        "GL-TESTCOV-vmware-config-kernel-cmdline-console",
    ]
)
@pytest.mark.feature("lima or metal or vmware")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_console_configuration_in_cmdline_bautrates(kernel_cmdline: List[str]):
    """Verify console parameters are present in the running kernel command line for bautrates."""
    assert (
        "console=ttyS0,115200" in kernel_cmdline
    ), "Serial console (ttyS0,115200) not found in kernel cmdline"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-kvm-config-kernel-cmdline-console",
    ]
)
@pytest.mark.feature("kvm")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
@pytest.mark.arch("amd64")
def test_console_configuration_in_cmdline_kvm_earlycon_amd64(kernel_cmdline: List[str]):
    """Verify earlycon parameters are present in the running kernel command line for KVM on AMD64."""
    assert (
        "earlycon=ttyS0,115200n8" in kernel_cmdline
    ), "Early Serial console (ttyS0,115200n8) not found in kernel cmdline"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-kvm-config-kernel-cmdline-console",
    ]
)
@pytest.mark.feature("kvm")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
@pytest.mark.arch("arm64")
def test_console_configuration_in_cmdline_kvm_earlycon_aarch64(
    kernel_cmdline: List[str],
):
    """Verify earlycon parameters are present in the running kernel command line for KVM on ARM64."""
    assert (
        "earlycon=pl011,mmio,0x09000000" in kernel_cmdline
    ), "Early Serial console (pl011,mmio,0x09000000) not found in kernel cmdline"
