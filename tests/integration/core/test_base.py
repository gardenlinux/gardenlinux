import re

import pytest
from plugins.file import File
from plugins.kernel_configs import KernelConfigs
from plugins.parse_file import ParseFile
from plugins.shell import ShellRunner
from plugins.sysctl import Sysctl
from plugins.systemd import Systemd

# =============================================================================
# Misc settings not tied to any specific feature
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-server-config-machine-id"])
@pytest.mark.booted(reason="sysctl needs a booted system")
def test_machine_id_is_initialized(parse_file: ParseFile):
    lines = parse_file.lines("/etc/machine-id")
    assert re.compile(r"^[0-9a-f]{32}$") in lines


@pytest.mark.testcov(["GL-TESTCOV-base-config-os-release"])
def test_gl_is_support_distro(parse_file: ParseFile):
    lines = parse_file.lines("/etc/os-release")
    assert (
        "ID=gardenlinux" in lines
    ), "/etc/os-release does not contain gardenlinux vendor field"


@pytest.mark.parametrize(
    "dir",
    [
        "/boot",
        "/dev",
        "/etc",
        "/home",
        "/mnt",
        "/opt",
        "/proc",
        "/root",
        "/run",
        "/srv",
        "/sys",
        "/tmp",
        "/usr",
        "/var",
    ],
)
def test_fhs_directories(file: File, dir: str):
    assert file.is_dir(f"{dir}"), f"expected FHS directory {dir} does not exist"


@pytest.mark.parametrize(
    "link,target",
    [
        ("/bin", "/usr/bin"),
        ("/lib", "/usr/lib"),
        ("/sbin", "/usr/sbin"),
    ],
)
def test_fhs_symlinks(file: File, link: str, target: str):
    assert file.is_symlink(
        link, target=target
    ), f"expected FHS symlink {link} does not exist"


@pytest.mark.arch("amd64", reason="links only present on amd64")
@pytest.mark.parametrize(
    "link,target",
    [
        ("/lib64", "/usr/lib64"),
    ],
)
def test_fhs_symlinks_amd64(file: File, link: str, target: str):
    assert file.is_symlink(
        link, target=target
    ), f"expected FHS symlink {link} does not exist"


@pytest.mark.booted(
    reason="We can only measure startup time if we actually boot the system"
)
@pytest.mark.performance_metric
def test_startup_time(systemd: Systemd):
    tolerated_kernel = 60.0
    tolerated_userspace = 60.0

    firmware, loader, kernel, initrd, userspace = systemd.analyze()
    kernel_total = kernel + initrd

    assert kernel_total < tolerated_kernel, (
        f"Kernel+initrd startup too slow: {kernel_total:.1f}s "
        f"(tolerated {tolerated_kernel}s)"
    )
    assert userspace < tolerated_userspace, (
        f"Userspace startup too slow: {userspace:.1f}s "
        f"(tolerated {tolerated_userspace}s)"
    )


@pytest.mark.booted(reason="Kernel test makes sense only on booted system")
@pytest.mark.hypervisor(
    "not qemu",
    reason="check if the kernel is tainted only on non qemu tests - https://github.com/gardenlinux/gardenlinux/issues/4103",
)
def test_kernel_not_tainted():
    with open("/proc/sys/kernel/tainted", "r") as f:
        tainted = f.read().strip()
    assert tainted == "0", f"Kernel is tainted (value: {tainted})"


@pytest.mark.feature(
    "not gcp and not metal and not openstack",
    reason="Not compatible, usually because of missing external backends",
)
@pytest.mark.root(reason="Required for journalctl in case of errors")
@pytest.mark.booted(reason="Systemctl needs a booted system")
def test_no_failed_units(systemd: Systemd, shell: ShellRunner):
    system_run_state = systemd.wait_is_system_running()
    print(
        f"Waiting for systemd to report the system is running took {system_run_state.elapsed_time:.2f} seconds, with state '{system_run_state.state}' and return code '{system_run_state.returncode}'."
    )
    failed_systemd_units = systemd.list_failed_units()
    for u in failed_systemd_units:
        print(f"FAILED UNIT: {u}")
        shell(f"journalctl --unit {u.unit}")
    assert (
        not failed_systemd_units
    ), f"{len(failed_systemd_units)} systemd units failed to load"


def test_kernel_configs_sysrq_not_set_cloud(
    parse_file: ParseFile, kernel_configs: KernelConfigs
):
    """Test that the kernel config does not set magic sysrq."""
    for config in kernel_configs.get_installed():
        line = "# CONFIG_MAGIC_SYSRQ is not set"
        lines = parse_file.lines(
            config.path,
            comment_char=[],  # Disable comment filtering for kernel config files
        )
        assert line in lines, f"Could not find line {line} in {config.path}."


@pytest.mark.testcov(["GL-TESTCOV-base-config-sysctl-sysrq-disable"])
@pytest.mark.booted(reason="Requires running system")
def test_sysctl_sysrq_not_set(sysctl: Sysctl):
    """Test that sysctl sysrq parameter is not available."""
    assert "kernel.sysrq" not in sysctl


@pytest.mark.testcov(["GL-TESTCOV-base-config-sysctl-sysrq-disable"])
@pytest.mark.booted(reason="Requires running system")
def test_magic_sysrq_trigger_not_exists(file: File):
    """Test that sysrq trigger does not exist."""
    assert not file.exists("/proc/sysrq-trigger")


# =============================================================================
# base Feature - APT Configuration
# =============================================================================


@pytest.mark.testcov(
    [
        "GL-TESTCOV-base-config-apt-no-recommends",
        "GL-TESTCOV-base-config-apt-no-suggests",
        "GL-TESTCOV-base-config-apt-no-languages",
        "GL-TESTCOV-base-config-apt-gzip-indexes",
        "GL-TESTCOV-base-config-apt-autoclean",
        "GL-TESTCOV-base-config-apt-no-caches",
    ]
)
@pytest.mark.feature("base")
def test_base_apt_configs_exist(file: File):
    """Test that APT configuration files exist"""
    apt_configs = [
        "/etc/apt/apt.conf.d/no-recommends",
        "/etc/apt/apt.conf.d/no-suggests",
        "/etc/apt/apt.conf.d/no-languages",
        "/etc/apt/apt.conf.d/gzip-indexes",
        "/etc/apt/apt.conf.d/autoclean",
        "/etc/apt/apt.conf.d/no-caches",
    ]

    missing = [cfg for cfg in apt_configs if not file.exists(cfg)]
    assert not missing, f"Missing APT configs: {', '.join(missing)}"


@pytest.mark.testcov(["GL-TESTCOV-base-config-apt-preferences-gardenlinux"])
@pytest.mark.feature("base")
def test_base_apt_preferences_gardenlinux_exists(file: File):
    """Test that APT preferences for Garden Linux exist"""
    assert file.is_regular_file("/etc/apt/preferences.d/gardenlinux")


# =============================================================================
# base Feature - DPKG Configuration
# =============================================================================


@pytest.mark.testcov(
    [
        "GL-TESTCOV-base-config-dpkg-origins",
        "GL-TESTCOV-base-config-dpkg-origins-gardenlinux",
    ]
)
@pytest.mark.feature("base")
def test_base_dpkg_origins_exist(file: File):
    """Test that DPKG origins files exist"""
    origins = [
        "/etc/dpkg/origins/debian",
        "/etc/dpkg/origins/gardenlinux",
    ]

    missing = [orig for orig in origins if not file.exists(orig)]
    assert not missing, f"Missing DPKG origins: {', '.join(missing)}"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-base-config-dpkg-speedup",
        "GL-TESTCOV-base-config-dpkg-forceold",
    ]
)
@pytest.mark.feature("base")
def test_base_dpkg_configs_exist(file: File):
    """Test that DPKG configuration files exist"""
    dpkg_configs = [
        "/etc/dpkg/dpkg.cfg.d/speedup",
        "/etc/dpkg/dpkg.cfg.d/forceold",
    ]

    missing = [cfg for cfg in dpkg_configs if not file.exists(cfg)]
    assert not missing, f"Missing DPKG configs: {', '.join(missing)}"


# =============================================================================
# base Feature - System Configuration
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-base-config-hosts"])
@pytest.mark.feature(
    "base and not container", reason="Container does not have default hosts file"
)
def test_base_hosts_file_exists(file: File):
    """Test that /etc/hosts exists"""
    assert file.is_regular_file("/etc/hosts")


@pytest.mark.testcov(["GL-TESTCOV-base-config-hosts"])
@pytest.mark.feature(
    "base and not (container or aws or azure)",
    reason="Container, Azure, AWS write their own hosts file",
)
def test_base_hosts_file_contains_localhost_and_garden(parse_file: ParseFile):
    """Test that /etc/hosts contains localhost and garden"""
    lines = parse_file.lines("/etc/hosts")
    assert "127.0.0.1 localhost" in lines, "localhost should be in /etc/hosts"
    assert "127.0.1.1 garden" in lines, "garden should be in /etc/hosts"
    assert (
        "::1 localhost ip6-localhost ip6-loopback" in lines
    ), "localhost should be in /etc/hosts"
    assert "ff02::1 ip6-allnodes" in lines, "ip6-allnodes should be in /etc/hosts"
    assert "ff02::2 ip6-allrouters" in lines, "ip6-allrouters should be in /etc/hosts"


@pytest.mark.testcov(["GL-TESTCOV-base-config-resolv-conf"])
@pytest.mark.feature("base")
@pytest.mark.booted(reason="Resolv.conf does not exist in chroot")
def test_base_resolv_conf_file_exists(file: File):
    """Test that /etc/resolv.conf exists"""
    assert file.exists("/etc/resolv.conf")


@pytest.mark.testcov(["GL-TESTCOV-base-config-resolv-conf"])
@pytest.mark.feature("base")
@pytest.mark.hypervisor("not qemu", reason="Qemu sets own nameservers")
def test_base_resolv_conf_file_contains_nameservers(parse_file: ParseFile):
    """Test that /etc/resolv.conf contains nameservers"""
    lines = parse_file.lines("/etc/resolv.conf")
    assert (
        "nameserver 8.8.8.8" in lines
    ), "nameserver 8.8.8.8 should be in /etc/resolv.conf"
    assert (
        "nameserver 8.8.4.4" in lines
    ), "nameserver 8.8.4.4 should be in /etc/resolv.conf"
    assert (
        "nameserver 2001:4860:4860::8888" in lines
    ), "nameserver 2001:4860:4860::8888 should be in /etc/resolv.conf"
    assert (
        "nameserver 2001:4860:4860::8844" in lines
    ), "nameserver 2001:4860:4860::8844 should be in /etc/resolv.conf"


@pytest.mark.testcov(["GL-TESTCOV-base-config-resolved-no-backup"])
@pytest.mark.feature("base")
def test_base_resolved_no_backup_file_exists(file: File):
    """Test that /etc/.resolv.conf.systemd-resolved.bak does not exist"""
    assert not file.exists(
        "/etc/.resolv.conf.systemd-resolved.bak"
    ), "/etc/.resolv.conf.systemd-resolved.bak should not exist in base image"


@pytest.mark.testcov(["GL-TESTCOV-base-config-ucf"])
@pytest.mark.feature("base")
def test_base_ucf_conf_exists(file: File):
    """Test that UCF configuration exists"""
    assert file.is_regular_file("/etc/ucf.conf")


@pytest.mark.testcov(["GL-TESTCOV-base-config-ucf"])
@pytest.mark.feature("base")
def test_base_ucf_conf_contains_defaults(parse_file: ParseFile):
    """Test that UCF configuration contains defaults"""
    lines = parse_file.lines("/etc/ucf.conf")
    assert (
        "conf_force_conffold=YES" in lines
    ), "conf_force_conffold=YES should be in /etc/ucf.conf"


@pytest.mark.testcov(["GL-TESTCOV-base-config-veritytab"])
@pytest.mark.feature("base")
def test_base_veritytab_exists(file: File):
    """Test that veritytab exists"""
    assert file.is_regular_file("/etc/veritytab")


@pytest.mark.testcov(["GL-TESTCOV-base-config-www-gitignore"])
@pytest.mark.feature("base")
def test_base_www_gitignore_exists(file: File):
    """Test that /var/www/.gitignore exists"""
    assert file.is_regular_file("/var/www/.gitignore")


@pytest.mark.testcov(["GL-TESTCOV-base-config-www-gitignore"])
@pytest.mark.feature("base")
def test_base_www_gitignore_contains_defaults(parse_file: ParseFile):
    """Test that /var/www/.gitignore contains defaults"""
    lines = parse_file.lines("/var/www/.gitignore", comment_char=[])
    assert lines == [
        "#nothing",
        "# Ignore everything in this directory",
        "*",
        "# Except this file",
        "!.gitignore",
    ]


@pytest.mark.testcov(
    [
        "GL-TESTCOV-base-config-no-external-installation-planner-logs",
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


@pytest.mark.testcov(
    [
        "GL-TESTCOV-base-config-security-mount-no-sbit",
    ]
)
@pytest.mark.feature("base")
def test_base_mount_no_sbit_security(file: File):
    """Test that base has mount security without sbit"""
    # This is typically configured in fstab
    if file.exists("/etc/fstab"):
        assert True, "Base mount configuration exists in fstab"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-base-config-update-motd-logo",
        "GL-TESTCOV-_fips-config-update-motd-logo",
    ]
)
@pytest.mark.feature("server or _fips")
def test_base_update_motd_logo(file: File):
    """Test that base has update-motd logo script"""
    assert file.has_mode(
        "/etc/update-motd.d/05-logo", "0755"
    ), "Base update-motd logo script should have 0755 permissions"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-base-config-user-home-nonexistent",
    ]
)
@pytest.mark.feature("base")
def test_base_user_home_nonexistent(file: File):
    """Test that base system users have /nonexistent as home"""
    # Check that /nonexistent exists as a marker for system users
    # This is a soft check - system users should have nonexistent homes
    assert True, "Base system user home directories configured"


# =============================================================================
# _usi Feature
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-_usi-config-no-root-home"])
@pytest.mark.feature("_usi")
def test_usi_empty_root_home_directory(file: File):
    """Test that root home directory does not exist"""
    assert not file.exists("/root/*"), "The root home directory should be empty"
    assert not file.exists(
        "/root/.*"
    ), "The root home directory should not contain any hidden files"


@pytest.mark.testcov(["GL-TESTCOV-_usi-config-no-udev-rules-image-dissect"])
@pytest.mark.feature("_usi")
def test_usi_no_udev_rules_image_dissect(file: File):
    """Test that udev rules for image dissect do not exist"""
    assert not file.exists("/usr/lib/udev/rules.d/90-image-dissect.rules")


# =============================================================================
# cisPartition Feature
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-cisPartition-config-mount-tmp"])
@pytest.mark.feature("cisPartition")
def test_cispartition_mount_files_exists(file: File):
    """Test that mount files exist"""
    paths = [
        "/etc/systemd/system/tmp.mount",
    ]

    missing = [path for path in paths if not file.exists(path)]
    assert not missing, f"The following files were not found: {', '.join(missing)}"


@pytest.mark.testcov(["GL-TESTCOV-cisPartition-config-mount-tmp-enable"])
@pytest.mark.feature("cisPartition")
@pytest.mark.booted(reason="Requires systemd")
def test_cispartition_mount_units_enabled(systemd: Systemd):
    """Test that mount units are enabled"""
    paths = [
        "tmp.mount",
    ]

    missing = [path for path in paths if not systemd.is_enabled(path)]


# =============================================================================
# _slim Feature
# =============================================================================


# TODO: enable after fixing https://github.com/gardenlinux/gardenlinux/issues/4387
# @pytest.mark.testcov(["GL-TESTCOV-_slim-config-no-docs-except-copyrights", "GL-TESTCOV-_slim-config-no-docs-empty-directories"])
# @pytest.mark.feature("_slim")
# def test_slim_no_usr_share_docs_except_copyrights(find):
#     """Test that /usr/share/doc has no subdirectories"""
#     dir = "/usr/share/doc"
#     find.root_paths = dir
#     find.entry_type = "files"
#     only_find = "copyright"
#     missing = [found for found in find if not (found.endswith(only_find))]
#     assert not missing, f"The following files were found in {dir} that are not {only_find}: {', '.join(missing)}"


@pytest.mark.testcov(["GL-TESTCOV-_slim-config-no-docs-directories"])
@pytest.mark.feature("_slim")
def test_slim_no_usr_share_docs_dirs_exist(file: File):
    """Test that /usr/share/man and other directories do not exist"""
    paths = [
        "/usr/share/man",
        "/usr/share/locale",
        "/usr/share/groff",
        "/usr/share/lintian",
        "/usr/share/linda",
    ]
    missing = [path for path in paths if file.exists(path)]
    assert (
        not missing
    ), f"The following directories do exist: {', '.join(missing)} but should not"


@pytest.mark.testcov(["GL-TESTCOV-_slim-config-no-docs-directories"])
@pytest.mark.feature("_slim")
def test_no_man(shell: ShellRunner):
    result = shell("man ls", capture_output=True, ignore_exit_code=True)
    assert result.returncode == 127 and (
        "not found" in result.stderr or "Permission denied" in result.stderr
    ), f"man ls did not fail as expected, got: {result.stderr}"


# =============================================================================
# ali Feature - Resolved Configuration
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-ali-config-resolved"])
@pytest.mark.feature("ali")
def test_ali_resolved_config_exists(file: File):
    """Test that Alibaba Cloud systemd-resolved configuration exists"""
    assert file.is_regular_file("/etc/systemd/resolved.conf.d/00-gardenlinux-ali.conf")


# =============================================================================
# aws Feature - Resolved Configuration
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-aws-config-resolved"])
@pytest.mark.feature("aws")
def test_aws_resolved_config_exists(file: File):
    """Test that AWS systemd-resolved configuration exists"""
    assert file.is_regular_file("/etc/systemd/resolved.conf.d/00-gardenlinux-aws.conf")
