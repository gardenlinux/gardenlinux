"""Test kernel command line console configuration."""

from typing import List

import pytest
from plugins.kernel_cmdline import kernel_cmdline

# =============================================================================
# _trustedboot Feature Kernel Command Line
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-_trustedboot-config-kernel-cmdline-no-rd-shell"])
@pytest.mark.feature("_trustedboot")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_trustedboot_kernel_cmdline(kernel_cmdline: List[str]):
    """Verify kernel command line parameters are present in the running kernel command line for Trusted Boot"""
    required_params = ["rd.shell=0", "rd.emergency=poweroff", "systemd.gpt_auto=0"]
    missing = [param for param in required_params if param not in kernel_cmdline]
    assert (
        not missing
    ), f"The following kernel cmdline parameters were not found: {', '.join(missing)}"


# =============================================================================
# _usi Feature Kernel Command Line
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-_usi-config-kernel-cmdline-no-gpt-auto"])
@pytest.mark.feature("_usi")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_usi_kernel_cmdline(kernel_cmdline: List[str]):
    """Verify kernel command line parameters are present in the running kernel command line for USI"""
    required_params = ["systemd.gpt_auto=0"]
    missing = [param for param in required_params if param not in kernel_cmdline]
    assert (
        not missing
    ), f"The following kernel cmdline parameters were not found: {', '.join(missing)}"


# =============================================================================
# ali Feature Kernel Command Line
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-ali-config-kernel-cmdline-console"])
@pytest.mark.feature("ali")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_console_configuration_in_cmdline_ali(kernel_cmdline: List[str]):
    """Verify console parameters are present in the running kernel command line for Alibaba Cloud."""
    assert (
        "console=tty0" in kernel_cmdline
    ), "Virtual console (tty0) not found in kernel cmdline"
    assert any(
        param.startswith("console=ttyS0") for param in kernel_cmdline
    ), "Serial console (ttyS0) not found in kernel cmdline"


# =============================================================================
# aws Feature Kernel Command Line
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-aws-config-kernel-cmdline-console"])
@pytest.mark.feature("aws")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_console_configuration_in_cmdline_aws(kernel_cmdline: List[str]):
    """Verify console parameters are present in the running kernel command line for AWS."""
    assert (
        "console=tty0" in kernel_cmdline
    ), "Virtual console (tty0) not found in kernel cmdline"
    assert any(
        param.startswith("console=ttyS0") for param in kernel_cmdline
    ), "Serial console (ttyS0) not found in kernel cmdline"


# =============================================================================
# azure Feature Kernel Command Line
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-azure-config-kernel-cmdline-console"])
@pytest.mark.feature("azure")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_console_configuration_in_cmdline_azure(kernel_cmdline: List[str]):
    """Verify console parameters are present in the running kernel command line for Azure."""
    assert (
        "console=tty0" in kernel_cmdline
    ), "Virtual console (tty0) not found in kernel cmdline"
    assert any(
        param.startswith("console=ttyS0") for param in kernel_cmdline
    ), "Serial console (ttyS0) not found in kernel cmdline"


# =============================================================================
# gcp Feature Kernel Command Line
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-gcp-config-kernel-cmdline-console"])
@pytest.mark.feature("gcp")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_console_configuration_in_cmdline_gcp(kernel_cmdline: List[str]):
    """Verify console parameters are present in the running kernel command line for GCP."""
    assert (
        "console=tty0" in kernel_cmdline
    ), "Virtual console (tty0) not found in kernel cmdline"
    assert any(
        param.startswith("console=ttyS0") for param in kernel_cmdline
    ), "Serial console (ttyS0) not found in kernel cmdline"


# =============================================================================
# gdch Feature Kernel Command Line
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-gdch-config-kernel-cmdline-console"])
@pytest.mark.feature("gdch")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_console_configuration_in_cmdline_gdch(kernel_cmdline: List[str]):
    """Verify console parameters are present in the running kernel command line for GDCH.

    Note: GDCH only configures ttyS0 serial console, not tty0 virtual console.
    """
    assert any(
        param.startswith("console=ttyS0") for param in kernel_cmdline
    ), "Serial console (ttyS0) not found in kernel cmdline"


# =============================================================================
# kvm Feature Kernel Command Line
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-kvm-config-kernel-cmdline-console"])
@pytest.mark.feature("kvm")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
@pytest.mark.arch("amd64")
def test_console_configuration_in_cmdline_kvm_amd64(kernel_cmdline: List[str]):
    """Verify console parameters are present in the running kernel command line for KVM on AMD64."""
    assert (
        "console=tty0" in kernel_cmdline
    ), "Virtual console (tty0) not found in kernel cmdline"
    assert any(
        param.startswith("console=ttyS0") for param in kernel_cmdline
    ), "Serial console (ttyS0) not found in kernel cmdline"


@pytest.mark.setting_ids(
    [
        "GL-SET-kvm-config-kernel-cmdline-console",
    ]
)
@pytest.mark.feature("kvm")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
@pytest.mark.arch("amd64")
def test_console_configuration_in_cmdline_kvm_earlyprintk_amd64(
    kernel_cmdline: List[str],
):
    """Verify earlyprintk parameters are present in the running kernel command line for KVM on AMD64."""
    assert (
        "earlyprintk=ttyS0,115200n8" in kernel_cmdline
    ), "Early Serial console (earlyprintk=ttyS0,115200n8) not found in kernel cmdline"


@pytest.mark.setting_ids(
    [
        "GL-SET-kvm-config-kernel-cmdline-console",
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


# =============================================================================
# kvm Feature Kernel Command Line
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-kvm-config-kernel-cmdline-console"])
@pytest.mark.feature("kvm")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
@pytest.mark.arch("arm64")
def test_console_configuration_in_cmdline_kvm_aarch64(kernel_cmdline: List[str]):
    """Verify console parameters are present in the running kernel command line for KVM on ARM64."""
    assert (
        "console=tty0" in kernel_cmdline
    ), "Virtual console (tty0) not found in kernel cmdline"
    assert any(
        param.startswith("console=ttyAMA0") for param in kernel_cmdline
    ), "Serial console (ttyAMA0) not found in kernel cmdline"


# =============================================================================
# lima Feature Kernel Command Line
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-lima-config-kernel-cmdline-console"])
@pytest.mark.feature("lima")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_console_configuration_in_cmdline_lima(kernel_cmdline: List[str]):
    """Verify console parameters are present in the running kernel command line for Lima."""
    assert (
        "console=tty0" in kernel_cmdline
    ), "Virtual console (tty0) not found in kernel cmdline"
    assert any(
        param.startswith("console=ttyS0") for param in kernel_cmdline
    ), "Serial console (ttyS0) not found in kernel cmdline"


@pytest.mark.setting_ids(
    [
        "GL-SET-lima-config-kernel-cmdline-console",
    ]
)
@pytest.mark.feature("lima")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_console_configuration_in_cmdline_lima_bautrates(kernel_cmdline: List[str]):
    """Verify console bautrates configuration parameters are present in the running kernel command line for Lima."""
    assert (
        "console=ttyS0,115200" in kernel_cmdline
    ), "Serial console (ttyS0,115200) not found in kernel cmdline"


# =============================================================================
# metal Feature Kernel Command Line
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-metal-config-kernel-cmdline-console"])
@pytest.mark.feature("metal")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_console_configuration_in_cmdline_metal(kernel_cmdline: List[str]):
    """Verify console parameters are present in the running kernel command line for Metal."""
    assert (
        "console=tty0" in kernel_cmdline
    ), "Virtual console (tty0) not found in kernel cmdline"
    assert any(
        param.startswith("console=ttyS0") for param in kernel_cmdline
    ), "Serial console (ttyS0) not found in kernel cmdline"


@pytest.mark.setting_ids(
    [
        "GL-SET-metal-config-kernel-cmdline-console",
    ]
)
@pytest.mark.feature("metal")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_console_configuration_in_cmdline_metal_bautrates(kernel_cmdline: List[str]):
    """Verify console bautrates configuration parameters are present in the running kernel command line for Metal."""
    assert (
        "console=ttyS0,115200" in kernel_cmdline
    ), "Serial console (ttyS0,115200) not found in kernel cmdline"


# =============================================================================
# openstack Feature Kernel Command Line
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-openstack-config-kernel-cmdline-console"])
@pytest.mark.feature("openstack")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_console_configuration_in_cmdline_openstack(kernel_cmdline: List[str]):
    """Verify console parameters are present in the running kernel command line for OpenStack."""
    assert (
        "console=tty0" in kernel_cmdline
    ), "Virtual console (tty0) not found in kernel cmdline"
    assert any(
        param.startswith("console=ttyS0") for param in kernel_cmdline
    ), "Serial console (ttyS0) not found in kernel cmdline"


# =============================================================================
# vmware Feature Kernel Command Line
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-vmware-config-kernel-cmdline-console"])
@pytest.mark.feature("vmware")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_console_configuration_in_cmdline_vmware(kernel_cmdline: List[str]):
    """Verify console parameters are present in the running kernel command line for VMware."""
    assert (
        "console=tty0" in kernel_cmdline
    ), "Virtual console (tty0) not found in kernel cmdline"
    assert any(
        param.startswith("console=ttyS0") for param in kernel_cmdline
    ), "Serial console (ttyS0) not found in kernel cmdline"


@pytest.mark.setting_ids(
    [
        "GL-SET-vmware-config-kernel-cmdline-console",
    ]
)
@pytest.mark.feature("vmware")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_console_configuration_in_cmdline_vmware_bautrates(kernel_cmdline: List[str]):
    """Verify console bautrates configuration parameters are present in the running kernel command line for VMware."""
    assert (
        "console=ttyS0,115200" in kernel_cmdline
    ), "Serial console (ttyS0,115200) not found in kernel cmdline"
