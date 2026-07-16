from typing import List

import pytest
from plugins.file import File
from plugins.initrd import Initrd

# =============================================================================
# _trustedboot Feature
# =============================================================================


@pytest.mark.security_id(1027)
@pytest.mark.booted(reason="Requires booted VM to check SecureBoot via efivars")
@pytest.mark.feature("_trustedboot")
def test_secureboot_enabled(efivars):
    """Ensure SecureBoot is enabled by reading the SecureBoot efivar directly.

    This test reads the raw efivar file for the EFI global variable GUID and
    verifies that the SecureBoot variable's value byte is 1 (enabled). The
    test fails if the efivar file is missing or malformed.
    """
    # EFI_GLOBAL_VARIABLE GUID used for SecureBoot and many other variables
    EFI_GLOBAL_VARIABLE = "8be4df61-93ca-11d2-aa0d-00e098032b8c"

    try:
        data = efivars[EFI_GLOBAL_VARIABLE]["SecureBoot"]
    except KeyError:
        pytest.fail("SecureBoot variable not found in efivars")

    # efivar file format: 4 bytes attributes + value bytes
    if len(data) < 5:
        pytest.fail("SecureBoot efivar content too short or malformed")

    # value byte follows 4-byte attributes
    value = data[4]
    assert value == 1, f"SecureBoot is not enabled (value={value})"


# =============================================================================
# _usi Feature
# =============================================================================


@pytest.mark.testcov(
    [
        "GL-TESTCOV-_usi-config-update-motd-secureboot"
        "GL-TESTCOV-_usi-config-script-update-kernel-cmdline"
        "GL-TESTCOV-_usi-config-script-enroll-gardenlinux-secureboot-keys"
    ]
)
@pytest.mark.feature("_usi")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test__usi_files(file: File):
    """Test that files are present in initrd"""
    paths = [
        "/etc/update-motd.d/25-secureboot",
        "/usr/local/sbin/update-kernel-cmdline",
        "/usr/sbin/enroll-gardenlinux-secureboot-keys",
    ]

    missing = [path for path in paths if not file.exists(path)]
    assert not missing, f"The following files were not found: {', '.join(missing)}"


# =============================================================================
# _unsigned or _trustedboot Feature
# =============================================================================


@pytest.mark.testcov(
    [
        "GL-TESTCOV-_unsigned-config-efi-binary-exists",
        "GL-TESTCOV-_trustedboot-config-efi-binary-exists",
    ]
)
@pytest.mark.feature("_unsigned or _trustedboot")
@pytest.mark.booted(reason="Chroot environments have no populted '/efi' directory")
@pytest.mark.arch("amd64")
def test_amd64_efi_binary_exists(file: File):
    """Test that unsigned has EFI binary"""
    efi_path = "/efi/EFI/BOOT/BOOTX64.EFI"
    exists = file.exists(efi_path)
    assert exists, f"EFI boot binary should exist: {efi_path}"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-_unsigned-config-efi-binary-exists",
        "GL-TESTCOV-_trustedboot-config-efi-binary-exists",
    ]
)
@pytest.mark.feature("_unsigned or _trustedboot")
@pytest.mark.booted(reason="Chroot environments have no populted '/efi' directory")
@pytest.mark.arch("arm64")
def test_arm64_efi_binary_exists(file: File):
    """Test that unsigned has EFI binary"""
    efi_path = "/efi/EFI/BOOT/BOOTAA64.EFI"
    exists = file.exists(efi_path)
    assert exists, f"EFI boot binary should exist: {efi_path}"


# =============================================================================
# _trustedboot Feature Kernel Command Line
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-_trustedboot-config-kernel-cmdline-no-rd-shell"])
@pytest.mark.feature("_trustedboot")
def test_trustedboot_kernel_cmdline_no_rd_shell_exists(file: File):
    """Test that Trusted Boot kernel cmdline configuration exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/99-no-rd-shell.cfg")


@pytest.mark.testcov(["GL-TESTCOV-_trustedboot-config-kernel-cmdline-no-rd-shell"])
@pytest.mark.feature("_trustedboot")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_trustedboot_kernel_cmdline_no_rd_shell(kernel_cmdline: List[str]):
    """Verify kernel command line parameters are present in the running kernel command line for Trusted Boot"""
    required_params = ["rd.shell=0", "rd.emergency=poweroff", "systemd.gpt_auto=0"]
    missing = [param for param in required_params if param not in kernel_cmdline]
    assert (
        not missing
    ), f"The following kernel cmdline parameters were not found: {', '.join(missing)}"


# =============================================================================
# _trustedboot Feature Initrd
# =============================================================================


@pytest.mark.testcov(
    [
        "GL-TESTCOV-_trustedboot-service-initrd-local-fs-target-requires-check-secureboot-unit",
        "GL-TESTCOV-_trustedboot-service-initrd-emergency-unit",
        "GL-TESTCOV-_trustedboot-script-initrd-check-secureboot",
    ]
)
@pytest.mark.feature("_trustedboot")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_trustedboot_initrd_files(initrd: Initrd):
    """Test that files are present in initrd"""
    paths = [
        "etc/systemd/system/local-fs.target.requires/check-secureboot.service",
        "etc/systemd/system/emergency.service",
        "usr/bin/check-secureboot",
    ]

    missing = [path for path in paths if not initrd.contains_file(path)]
    assert (
        not missing
    ), f"The following files were not found in initrd: {', '.join(missing)}"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-_trustedboot-config-kernel-cmdline-no-rd-shell",
    ]
)
@pytest.mark.feature("_trustedboot")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_trustedboot_kernel_cmdline(kernel_cmdline: List[str]):
    """Verify kernel command line parameters are present in the running kernel command line for Trusted Boot"""
    required_params = ["rd.shell=0", "rd.emergency=poweroff", "systemd.gpt_auto=0"]
    missing = [param for param in required_params if param not in kernel_cmdline]
    assert (
        not missing
    ), f"The following kernel cmdline parameters were not found: {', '.join(missing)}"


@pytest.mark.testcov(["GL-TESTCOV-_trustedboot-service-initrd-emergency-unit"])
@pytest.mark.feature("_trustedboot")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_trustedboot_check_initrd_emergency_unit_exists(initrd: Initrd):
    """Test that emergency.service unit file exists in initrd"""
    assert initrd.contains_file("etc/systemd/system/emergency.service")


@pytest.mark.testcov(
    [
        "GL-TESTCOV-_trustedboot-service-initrd-local-fs-target-requires-check-secureboot-unit"
    ]
)
@pytest.mark.feature("_trustedboot")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_trustedboot_check_initrd_local_fs_target_requires_check_secureboot_unit(
    initrd: Initrd,
):
    """Test that check-secureboot.service unit file exists in local-fs.target.requires"""
    assert initrd.contains_file(
        "etc/systemd/system/local-fs.target.requires/check-secureboot.service"
    )


# =============================================================================
# _usi Feature Kernel Command Line
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-_usi-config-kernel-cmdline-no-gpt-auto"])
@pytest.mark.feature("_usi")
def test_usi_kernel_cmdline_no_gpt_auto_exists(file: File):
    """Test that USI kernel cmdline configuration exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/99-no-gpt-auto.cfg")


@pytest.mark.testcov(["GL-TESTCOV-_usi-config-kernel-cmdline-no-gpt-auto"])
@pytest.mark.feature("_usi")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_usi_kernel_cmdline(kernel_cmdline: List[str]):
    """Verify kernel command line parameters are present in the running kernel command line for USI"""
    required_params = ["systemd.gpt_auto=0"]
    missing = [param for param in required_params if param not in kernel_cmdline]
    assert (
        not missing
    ), f"The following kernel cmdline parameters were not found: {', '.join(missing)}"
