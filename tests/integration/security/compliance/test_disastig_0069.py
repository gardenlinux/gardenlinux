import pytest

"""
Ref: SRG-OS-000138-GPOS-00069

Verify operating systems prevents unauthorized and unintended information
transfer via shared system resources.
"""


# temporary files
@pytest.mark.booted(reason="Mounts are present on a booted system")
def test_tmp_mount_is_configured_securely(shell):
    result = shell("findmnt -n -o 'OPTIONS' /tmp", capture_output=True)
    mount_options = set(result.stdout.split(","))
    required_mount_options = {"nosuid", "seclabel"}
    missing_mount_options = required_mount_options - mount_options
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
        config_found = [
            line
            for line in result.stdout.split("\n")
            if line.startswith(f"q {dir} 1777 root root")
        ]
        assert (
            len(config_found) == 1
        ), f"{dir} should be correctly configured in systemd-tmpfiles, got '{config_found}'"


# coredumps
def test_suid_binaries_cannot_create_coredumps(sysctl):
    sysctl.collect_sysctl_parameters()
    assert sysctl["fs.suid_dumpable"] == 0


# memory
# TODO: shouldn't ASLR be enabled for all flavors?
@pytest.mark.feature("cloud or (openstack and metal)")
def test_kernel_randomizes_virtual_memory_addresses(sysctl):
    sysctl.collect_sysctl_parameters()
    assert sysctl["kernel.randomize_va_space"] == 2
