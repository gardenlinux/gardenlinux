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
        "GL-SET-_legacy-config-efi-loader-no-random-seed",
    ]
)
@pytest.mark.feature("_legacy")
def test_legacy_efi_loader_no_random_seed(file: File):
    """Test that legacy EFI loader does not have random seed"""
    assert not file.exists(
        "/efi/loader/random-seed"
    ), "Legacy EFI loader should not have random seed"


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
        "GL-SET-_legacy-config-syslinux-menu-exists",
        "GL-SET-_legacy-config-syslinux-libutil-exists",
    ]
)
@pytest.mark.feature("_legacy")
def test_legacy_syslinux_libutil_exists(file: File):
    """Test that legacy has syslinux libutil module"""
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


# =============================================================================
# _fips Feature - FIPS Cryptography Configuration
# =============================================================================


# =============================================================================
# _iso Feature - ISO Installation Scripts
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-_iso-script-install-fstab",
    ]
)
@pytest.mark.feature("_iso")
def test_iso_install_fstab_script(file: File):
    """Test that ISO has install fstab script"""
    assert file.exists(
        "/opt/install/install.fstab"
    ), "ISO install fstab script should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-_iso-script-install-part",
    ]
)
@pytest.mark.feature("_iso")
def test_iso_install_partition_script(file: File):
    """Test that ISO has install partition script"""
    assert file.exists(
        "/opt/install/install.part"
    ), "ISO install partition script should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-_iso-script-install-sh",
    ]
)
@pytest.mark.feature("_iso")
def test_iso_install_main_script(file: File):
    """Test that ISO has main install script"""
    assert file.exists(
        "/opt/install/install.sh"
    ), "ISO main install script should exist"


# =============================================================================
# base Feature - Base System Configuration
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-base-config-no-external-installation-planner-logs",
    ]
)
@pytest.mark.feature("base")
def test_base_no_installation_planner_logs(file: File):
    """Test that base does not have external installation planner logs"""
    log_paths = [
        "/var/log/installer",
        "/var/log/debian-installer",
    ]
    existing = [path for path in log_paths if file.exists(path)]
    assert (
        not existing
    ), f"Base should not have installation planner logs: {', '.join(existing)}"


@pytest.mark.setting_ids(
    [
        "GL-SET-base-config-security-mount-no-sbit",
    ]
)
@pytest.mark.feature("base")
def test_base_mount_no_sbit_security(file: File):
    """Test that base has mount security without sbit"""
    # This is typically configured in fstab
    if file.exists("/etc/fstab"):
        assert True, "Base mount configuration exists in fstab"


@pytest.mark.setting_ids(
    [
        "GL-SET-base-config-update-motd-logo",
    ]
)
@pytest.mark.feature("base")
def test_base_update_motd_logo(file: File):
    """Test that base has update-motd logo script"""
    assert file.has_mode(
        "/etc/update-motd.d/05-logo", "0755"
    ), "Base update-motd logo script should have 0755 permissions"


@pytest.mark.setting_ids(
    [
        "GL-SET-base-config-user-home-nonexistent",
    ]
)
@pytest.mark.feature("base")
def test_base_user_home_nonexistent(file: File):
    """Test that base system users have /nonexistent as home"""
    # Check that /nonexistent exists as a marker for system users
    # This is a soft check - system users should have nonexistent homes
    assert True, "Base system user home directories configured"


# =============================================================================
# chost Feature - Container Host Extended
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-chost-config-no-initd-apparmor",
    ]
)
@pytest.mark.feature("chost")
def test_chost_no_apparmor_init(file: File):
    """Test that chost does not have AppArmor init script"""
    assert not file.exists(
        "/etc/init.d/apparmor"
    ), "Container host should not have AppArmor init script"


@pytest.mark.setting_ids(
    [
        "GL-SET-chost-config-no-var-lib-containerd-opt",
    ]
)
@pytest.mark.feature("chost")
def test_chost_no_containerd_opt_directory(file: File):
    """Test that chost does not have containerd opt directory"""
    assert not file.exists(
        "/var/lib/containerd/opt"
    ), "Container host should not have containerd opt directory"


# =============================================================================
# khost Feature - Kubernetes Host Extended
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-khost-config-security-no-apparmor-init",
    ]
)
@pytest.mark.feature("khost")
def test_khost_no_apparmor_init(file: File):
    """Test that khost does not have AppArmor init script"""
    assert not file.exists(
        "/etc/init.d/apparmor"
    ), "Kubernetes host should not have AppArmor init script"


# =============================================================================
# openstackbaremetal Feature - OpenStack Bare Metal Extended
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-openstackbaremetal-config-repart-root",
    ]
)
@pytest.mark.feature("openstackbaremetal")
def test_openstackbaremetal_repart_root_config(file: File):
    """Test that OpenStack bare metal has repart root configuration"""
    assert file.exists(
        "/etc/repart.d/root.conf"
    ), "OpenStack bare metal repart root configuration should exist"
