from configparser import MissingSectionHeaderError

import pytest
from plugins.file import File
from plugins.kernel_versions import KernelVersions
from plugins.parse_file import ParseFile

# =============================================================================
# _legacy Feature - Legacy Bootloader Support
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-_legacy-config-syslinux-bootloader-entries",
    ]
)
@pytest.mark.feature("_legacy")
def test_legacy_syslinux_bootloader_entries(
    file: File, kernel_versions: KernelVersions
):
    """Test that legacy has syslinux bootloader entries"""
    running_kernel = kernel_versions.get_running()
    assert file.exists(
        f"/efi/loader/entries/Default-{running_kernel.version}.conf"
    ), "Legacy syslinux bootloader entries should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-_legacy-config-syslinux-menu-amd64-exists",
        "GL-SET-_legacy-config-syslinux-libutil-amd64-exists",
    ]
)
@pytest.mark.feature("_legacy")
@pytest.mark.arch("amd64")
def test_legacy_syslinux_libutil_exists(file: File):
    """Test that legacy and amd64 has syslinux libutil module"""
    paths = [
        "/efi/syslinux/menu.c32",
        "/efi/syslinux/libutil.c32",
    ]
    missing = [path for path in paths if not file.exists(path)]
    assert (
        not missing
    ), f"Legacy syslinux files should exist but are missing: {', '.join(missing)}"


@pytest.mark.setting_ids(
    [
        "GL-SET-_legacy-script-update-bootloaders",
        "GL-SET-_legacy-script-update-kernel-cmdline",
        "GL-SET-_legacy-script-update-syslinux",
    ]
)
@pytest.mark.feature("_legacy")
def test_legacy_update_bootloaders_script(file: File):
    """Test that legacy has update-bootloaders script"""
    paths = [
        "/usr/local/sbin/update-bootloaders",
        "/usr/local/sbin/update-kernel-cmdline",
        "/usr/local/sbin/update-syslinux",
    ]
    missing = [path for path in paths if not file.exists(path)]
    assert (
        not missing
    ), f"Legacy scripts should exist but are missing: {', '.join(missing)}"
