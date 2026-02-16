"""Test kernel command line console configuration."""

from errno import EALREADY
from typing import List

import pytest
from plugins.file import File
from plugins.kernel_cmdline import kernel_cmdline

# =============================================================================
# _trustedboot Feature Kernel Command Line
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-_trustedboot-config-kernel-cmdline-no-rd-shell"])
@pytest.mark.feature("_trustedboot")
def test_trustedboot_kernel_cmdline_no_rd_shell_exists(file: File):
    """Test that Trusted Boot kernel cmdline configuration exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/99-no-rd-shell.cfg")


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
def test_usi_kernel_cmdline_no_gpt_auto_exists(file: File):
    """Test that USI kernel cmdline configuration exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/99-no-gpt-auto.cfg")


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
def test_ali_kernel_cmdline_console_exists(file: File):
    """Test that Alibaba Cloud kernel cmdline console configuration exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/10-console.cfg")


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
def test_aws_kernel_cmdline_console_exists(file: File):
    """Test that AWS kernel cmdline console configuration exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/10-console.cfg")


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


@pytest.mark.setting_ids(["GL-SET-aws-config-kernel-cmdline-nvme"])
@pytest.mark.feature("aws")
def test_aws_kernel_cmdline_nvme_exists(file: File):
    """Test that AWS nvme kernel cmdline configuration exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/70-nvme.cfg")


@pytest.mark.setting_ids(["GL-SET-aws-config-kernel-cmdline-nvme"])
@pytest.mark.feature("aws")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_nvme_configuration_in_cmdline_aws(kernel_cmdline: List[str]):
    """Verify nvme parameters are present in the running kernel command line for AWS."""
    assert (
        "nvme_core.io_timeout=4294967295" in kernel_cmdline
    ), "NVMe io timeout (nvme_core.io_timeout=4294967295) not found in kernel cmdline"


# =============================================================================
# azure Feature Kernel Command Line
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-azure-config-kernel-cmdline-console"])
@pytest.mark.feature("azure")
def test_azure_kernel_cmdline_console_exists(file: File):
    """Test that Azure kernel cmdline console configuration exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/10-console.cfg")


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


@pytest.mark.setting_ids(["GL-SET-azure-config-kernel-cmdline-nvme"])
@pytest.mark.feature("azure")
def test_azure_kernel_cmdline_nvme_exists(file: File):
    """Test that Azure nvme kernel cmdline configuration exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/45-nvme-timeout.cfg")


@pytest.mark.setting_ids(["GL-SET-azure-config-kernel-cmdline-nvme"])
@pytest.mark.feature("azure")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_nvme_configuration_in_cmdline_azure(kernel_cmdline: List[str]):
    """Verify nvme parameters are present in the running kernel command line for Azure."""
    assert (
        "nvme_core.io_timeout=240" in kernel_cmdline
    ), "NVMe io timeout (nvme_core.io_timeout=240) not found in kernel cmdline"


# =============================================================================
# Cloud Feature Kernel Command Line
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-cloud-config-kernel-cmdline-default"])
@pytest.mark.feature("cloud")
def test_cloud_kernel_cmdline_default_exists(file: File):
    """Test that cloud default kernel cmdline configuration exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/00-default.cfg")


@pytest.mark.setting_ids(["GL-SET-cloud-config-kernel-cmdline-default"])
@pytest.mark.feature("cloud")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_cloud_kernel_cmdline_default(kernel_cmdline: List[str]):
    """Verify default parameters are present in the running kernel command line for cloud."""

    required_params = ["rw", "earlyprintk=ttyS0,115200", "consoleblank=0"]
    missing = [param for param in required_params if param not in kernel_cmdline]
    assert (
        not missing
    ), f"The following kernel cmdline parameters were not found: {', '.join(missing)}"


@pytest.mark.setting_ids(
    ["GL-SET-cloud-config-kernel-cmdline-enable-swap-cgroup-accounting"]
)
@pytest.mark.feature("cloud")
def test_cloud_kernel_cmdline_swap_cgroup_exists(file: File):
    """Test that cloud swap cgroup accounting kernel cmdline configuration exists"""
    assert file.is_regular_file(
        "/etc/kernel/cmdline.d/40-enable-swap-cgroup-accounting.cfg"
    )


@pytest.mark.setting_ids(
    ["GL-SET-cloud-config-kernel-cmdline-enable-swap-cgroup-accounting"]
)
@pytest.mark.feature("cloud")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_cloud_kernel_cmdline_swap_cgroup(kernel_cmdline: List[str]):
    """Verify swap cgroup accounting parameters are present in the running kernel command line for cloud."""
    required_params = ["cgroup_enable=memory", "swapaccount=1"]
    missing = [param for param in required_params if param not in kernel_cmdline]
    assert (
        not missing
    ), f"The following kernel cmdline parameters were not found: {', '.join(missing)}"


@pytest.mark.setting_ids(["GL-SET-cloud-config-kernel-cmdline-timeout"])
@pytest.mark.feature("cloud")
def test_cloud_kernel_cmdline_timeout_exists(file: File):
    """Test that cloud timeout kernel cmdline configuration exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/60-timeout.cfg")


# TODO: Add test for timeout parameter
# @pytest.mark.setting_ids(["GL-SET-cloud-config-kernel-cmdline-timeout"])
# @pytest.mark.feature("cloud")
# @pytest.mark.booted(reason="kernel cmdline needs a booted system")
# def test_cloud_kernel_cmdline_timeout(kernel_cmdline: List[str]):
#     """Verify timeout parameters are present in the running kernel command line for cloud."""


# =============================================================================
# gcp Feature Kernel Command Line
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-gcp-config-kernel-cmdline-default"])
@pytest.mark.feature("gcp")
def test_gcp_kernel_cmdline_default_exists(file: File):
    """Test that GCP default kernel cmdline configuration exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/00-default.cfg")


# TODO: Clarify why we have 2 files setting the same kernel cmdline parameters
# @pytest.mark.setting_ids(["GL-SET-gcp-config-kernel-cmdline-default"])
# @pytest.mark.feature("gcp")
# @pytest.mark.booted(reason="kernel cmdline needs a booted system")
# def test_gcp_kernel_cmdline_default(kernel_cmdline: List[str]):
#     """Verify default parameters are present in the running kernel command line for GCP."""
#     required_params = ["console=tty0", "console=ttyS0,38400n8d", "consoleblank=0"]
#     missing = [param for param in required_params if param not in kernel_cmdline]
#     assert (
#         not missing
#     ), f"The following kernel cmdline parameters were not found: {', '.join(missing)}"


@pytest.mark.setting_ids(["GL-SET-gcp-config-kernel-cmdline-console"])
@pytest.mark.feature("gcp")
def test_gcp_kernel_cmdline_console_exists(file: File):
    """Test that GCP kernel cmdline console configuration exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/10-console.cfg")


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


@pytest.mark.setting_ids(["GL-SET-gdch-config-kernel-cmdline-default"])
@pytest.mark.feature("gdch")
def test_gdch_kernel_cmdline_default_exists(file: File):
    """Test that GDCH default kernel cmdline configuration exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/00-default.cfg")


# TODO: Clarify why we have 2 files setting the same kernel cmdline parameters
# @pytest.mark.setting_ids(["GL-SET-gdch-config-kernel-cmdline-default"])
# @pytest.mark.feature("gdch")
# @pytest.mark.booted(reason="kernel cmdline needs a booted system")
# def test_gdch_kernel_cmdline_default(kernel_cmdline: List[str]):
#     """Verify default parameters are present in the running kernel command line for GDCH."""
#     required_params = ["console=ttyS0,38400n8d", "consoleblank=0"]
#     missing = [param for param in required_params if param not in kernel_cmdline]
#     assert (
#         not missing
#     ), f"The following kernel cmdline parameters were not found: {', '.join(missing)}"


@pytest.mark.setting_ids(["GL-SET-gdch-config-kernel-cmdline-console"])
@pytest.mark.feature("gdch")
def test_gdch_kernel_cmdline_console_exists(file: File):
    """Test that GDCH kernel cmdline console configuration exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/10-console.cfg")


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
def test_kvm_kernel_cmdline_console_exists(file: File):
    """Test that KVM kernel cmdline console configuration exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/10-console.cfg")


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


@pytest.mark.setting_ids(["GL-SET-kvm-config-kernel-cmdline-ignition"])
@pytest.mark.feature("kvm")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_ignition_configuration_in_cmdline_kvm(kernel_cmdline: List[str]):
    """Verify ignition parameters are present in the running kernel command line for KVM."""
    assert (
        "ignition.firstboot=1 ignition.platform.id=qemu" in kernel_cmdline
    ), "Ignition (ignition.firstboot=1 ignition.platform.id=qemu) not found in kernel cmdline"


# =============================================================================
# lima Feature Kernel Command Line
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-lima-config-kernel-cmdline-default"])
@pytest.mark.feature("lima")
def test_lima_kernel_cmdline_default_exists(file: File):
    """Test that Lima default kernel cmdline configuration exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/00-default.cfg")


@pytest.mark.setting_ids(["GL-SET-lima-config-kernel-cmdline-default"])
@pytest.mark.feature("lima")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_lima_kernel_cmdline_default(kernel_cmdline: List[str]):
    """Verify default parameters are present in the running kernel command line for Lima."""
    required_params = ["rw", "earlyprintk=ttyS0,115200", "consoleblank=0"]
    missing = [param for param in required_params if param not in kernel_cmdline]
    assert (
        not missing
    ), f"The following kernel cmdline parameters were not found: {', '.join(missing)}"


@pytest.mark.setting_ids(["GL-SET-lima-config-kernel-cmdline-console"])
@pytest.mark.feature("lima")
def test_lima_kernel_cmdline_console_exists(file: File):
    """Test that Lima kernel cmdline console configuration exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/10-console.cfg")


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
@pytest.mark.setting_ids(["GL-SET-metal-config-kernel-cmdline-default"])
@pytest.mark.feature("metal")
def test_metal_kernel_cmdline_default_exists(file: File):
    """Test that Metal default kernel cmdline configuration exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/00-default.cfg")


@pytest.mark.setting_ids(["GL-SET-metal-config-kernel-cmdline-default"])
@pytest.mark.feature("metal")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_metal_kernel_cmdline_default(kernel_cmdline: List[str]):
    """Verify default parameters are present in the running kernel command line for Metal."""
    required_params = ["rw", "earlyprintk=ttyS0,115200", "consoleblank=0"]
    missing = [param for param in required_params if param not in kernel_cmdline]
    assert (
        not missing
    ), f"The following kernel cmdline parameters were not found: {', '.join(missing)}"


@pytest.mark.setting_ids(["GL-SET-metal-config-kernel-cmdline-console"])
@pytest.mark.feature("metal")
def test_metal_kernel_cmdline_console_exists(file: File):
    """Test that Metal console kernel cmdline configuration exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/10-console.cfg")


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
def test_openstack_kernel_cmdline_console_exists(file: File):
    """Test that OpenStack kernel cmdline console configuration exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/10-console.cfg")


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
# openstackbaremetal Feature Kernel Command Line
# =============================================================================


@pytest.mark.setting_ids(
    ["GL-SET-openstackbaremetal-config-kernel-cmdline-enable-swap-cgroup-accounting"]
)
@pytest.mark.feature("openstackbaremetal")
def test_openstackbaremetal_kernel_cmdline_enable_swap_cgroup_accounting_exists(
    file: File,
):
    """Test that OpenStack Bare Metal kernel cmdline enable swap cgroup accounting configuration exists"""
    assert file.is_regular_file(
        "/etc/kernel/cmdline.d/40-enable-swap-cgroup-accounting.cfg"
    )


@pytest.mark.setting_ids(
    ["GL-SET-openstackbaremetal-config-kernel-cmdline-enable-swap-cgroup-accounting"]
)
@pytest.mark.feature("openstackbaremetal")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_enable_swap_cgroup_accounting_configuration_in_cmdline_openstackbaremetal(
    kernel_cmdline: List[str],
):
    """Verify enable swap cgroup accounting parameters are present in the running kernel command line for OpenStack Bare Metal."""
    assert (
        "cgroup_enable=memory swapaccount=1" in kernel_cmdline
    ), "Enable swap cgroup accounting (cgroup_enable=memory swapaccount=1) not found in kernel cmdline"


# =============================================================================
# vmware Feature Kernel Command Line
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-vmware-config-kernel-cmdline-console"])
@pytest.mark.feature("vmware")
def test_vmware_kernel_cmdline_console_exists(file: File):
    """Test that VMware kernel cmdline console configuration exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/10-console.cfg")


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


@pytest.mark.setting_ids(["GL-SET-vmware-config-kernel-cmdline-ignition"])
@pytest.mark.feature("vmware")
def test_vmware_kernel_cmdline_ignition_exists(file: File):
    """Test that VMware kernel cmdline ignition configuration exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/50-ignition.cfg")


@pytest.mark.setting_ids(["GL-SET-vmware-config-kernel-cmdline-ignition"])
@pytest.mark.feature("vmware")
@pytest.mark.arch("amd64")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_ignition_configuration_in_cmdline_vmware_amd64(kernel_cmdline: List[str]):
    """Verify ignition parameters are present in the running kernel command line for VMware."""
    assert (
        "ignition.firstboot=1 ignition.platform.id=vmware" in kernel_cmdline
    ), "Ignition (ignition.firstboot=1 ignition.platform.id=vmware) not found in kernel cmdline"


@pytest.mark.setting_ids(
    [
        "GL-SET-vmware-config-kernel-cmdline-no-ignition-arm64",
    ]
)
@pytest.mark.feature("vmware")
@pytest.mark.arch("arm64")
def test_vmware_kernel_cmdline_no_ignition_arm64(file: File):
    """Test that VMware does not have ignition kernel cmdline for ARM64"""
    assert not file.exists(
        "/etc/kernel/cmdline.d/50-ignition.cfg"
    ), "ARM64 ignition config should not exist"


@pytest.mark.setting_ids(["GL-SET-vmware-config-kernel-cmdline-ignition"])
@pytest.mark.feature("vmware")
@pytest.mark.arch("arm64")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_no_ignition_configuration_in_cmdline_vmware_arm64(kernel_cmdline: List[str]):
    """Verify no ignition parameters are present in the running kernel command line for VMware."""
    assert (
        "ignition.firstboot=1 ignition.platform.id=vmware" not in kernel_cmdline
    ), "Ignition (ignition.firstboot=1 ignition.platform.id=vmware) found in kernel cmdline"
