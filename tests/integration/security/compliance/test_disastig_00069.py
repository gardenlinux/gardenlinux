import pytest
from plugins.parse import Lines

"""
Ref: SRG-OS-000138-GPOS-00069

Verify operating systems prevents unauthorized and unintended information
transfer via shared system resources.
"""


# -- temporary files
@pytest.mark.feature("not _selinux")
@pytest.mark.booted(reason="Mounts are present on a booted system")
def test_tmp_mount_is_configured_securely(mount):
    required_mount_options = {"nosuid"}

    real_mount_options = mount("/tmp").options
    missing_mount_options = required_mount_options - real_mount_options

    assert (
        not missing_mount_options
    ), f"Missing /tmp mount options: {missing_mount_options}"


@pytest.mark.feature("_selinux")
@pytest.mark.booted(reason="Mounts are present on a booted system")
def test_tmp_mount_is_configured_securely_and_with_selinux(mount):
    required_mount_options = {"nosuid", "seclabel"}

    real_mount_options = mount("/tmp").options
    missing_mount_options = required_mount_options - real_mount_options

    assert (
        not missing_mount_options
    ), f"Missing /tmp mount options: {missing_mount_options}"


def test_temp_directores_are_world_writable_and_have_sticky_bit_set(file):
    for dir in ["/tmp", "/var/tmp"]:
        assert file.is_dir(dir)
        assert file.has_mode(dir, "1777")


@pytest.mark.booted(reason="Systemd should be running")
def test_systemd_tmpfiles_configuration_is_sane(shell):
    result = shell("systemd-tmpfiles --cat-config", capture_output=True)
    for dir in ["/tmp", "/var/tmp"]:
        lines = Lines(result.stdout, comment_char="#")
        assert (
            f"q {dir} 1777 root root" in lines
        ), f"{dir} should be correctly configured in systemd-tmpfiles"


# -- coredumps
@pytest.mark.feature("disaSTIGmedium")
def test_suid_binaries_cannot_create_coredumps(sysctl):
    assert sysctl["fs.suid_dumpable"] == 0


# -- memory
@pytest.mark.feature("disaSTIGmedium")
def test_kernel_randomizes_virtual_memory_addresses(sysctl):
    assert sysctl["kernel.randomize_va_space"] == 2
