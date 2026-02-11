import glob

import pytest
from plugins.file import File
from plugins.parse_file import ParseFile

# =============================================================================
# base Feature - APT Configuration
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-base-config-apt-no-recommends",
        "GL-SET-base-config-apt-no-suggests",
        "GL-SET-base-config-apt-no-languages",
        "GL-SET-base-config-apt-gzip-indexes",
        "GL-SET-base-config-apt-autoclean",
        "GL-SET-base-config-apt-no-caches",
    ]
)
@pytest.mark.feature("base")
def test_base_apt_configs_exist(file: File):
    """Test that APT configuration files exist"""
    apt_configs = [
        "/etc/apt/apt.conf.d/99_norecommends",
        "/etc/apt/apt.conf.d/99_nosuggests",
        "/etc/apt/apt.conf.d/99_nolanguages",
        "/etc/apt/apt.conf.d/99_gzip-indexes",
        "/etc/apt/apt.conf.d/99_autoclean",
        "/etc/apt/apt.conf.d/99_no-cache",
    ]

    missing = [cfg for cfg in apt_configs if not file.exists(cfg)]
    assert not missing, f"Missing APT configs: {', '.join(missing)}"


@pytest.mark.setting_ids(["GL-SET-base-config-apt-preferences-gardenlinux"])
@pytest.mark.feature("base")
def test_base_apt_preferences_gardenlinux_exists(file: File):
    """Test that APT preferences for Garden Linux exist"""
    assert file.is_regular_file("/etc/apt/preferences.d/gardenlinux")


# =============================================================================
# base Feature - DPKG Configuration
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-base-config-dpkg-origins",
        "GL-SET-base-config-dpkg-origins-gardenlinux",
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


@pytest.mark.setting_ids(
    [
        "GL-SET-base-config-dpkg-speedup",
        "GL-SET-base-config-dpkg-forceold",
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


@pytest.mark.setting_ids(["GL-SET-base-config-hosts"])
@pytest.mark.feature("base")
def test_base_hosts_file_exists(file: File):
    """Test that /etc/hosts exists"""
    assert file.is_regular_file("/etc/hosts")


@pytest.mark.setting_ids(["GL-SET-base-config-hosts"])
@pytest.mark.feature("base")
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


@pytest.mark.setting_ids(["GL-SET-base-config-resolv-conf"])
@pytest.mark.feature("base")
def test_base_resolv_conf_file_exists(file: File):
    """Test that /etc/resolv.conf exists"""
    assert file.is_regular_file("/etc/resolv.conf")


@pytest.mark.setting_ids(["GL-SET-base-config-resolv-conf"])
@pytest.mark.feature("base")
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


@pytest.mark.setting_ids(["GL-SET-base-config-resolved-no-backup"])
@pytest.mark.feature("base")
def test_base_resolved_no_backup_file_exists(file: File):
    """Test that /etc/.resolv.conf.systemd-resolved.bak does not exist"""
    assert not file.exists(
        "/etc/.resolv.conf.systemd-resolved.bak"
    ), "/etc/.resolv.conf.systemd-resolved.bak should not exist in base image"


@pytest.mark.setting_ids(["GL-SET-base-config-ucf"])
@pytest.mark.feature("base")
def test_base_ucf_conf_exists(file: File):
    """Test that UCF configuration exists"""
    assert file.is_regular_file("/etc/ucf.conf")


@pytest.mark.setting_ids(["GL-SET-base-config-ucf"])
@pytest.mark.feature("base")
def test_base_ucf_conf_contains_defaults(parse_file: ParseFile):
    """Test that UCF configuration contains defaults"""
    lines = parse_file.lines("/etc/ucf.conf")
    assert (
        "conf_force_conffold=YES" in lines
    ), "conf_force_conffold=YES should be in /etc/ucf.conf"


@pytest.mark.setting_ids(["GL-SET-base-config-veritytab"])
@pytest.mark.feature("base")
def test_base_veritytab_exists(file: File):
    """Test that veritytab exists"""
    assert file.is_regular_file("/etc/veritytab")


@pytest.mark.setting_ids(["GL-SET-base-config-www-gitignore"])
@pytest.mark.feature("base")
def test_base_www_gitignore_exists(file: File):
    """Test that /var/www/.gitignore exists"""
    assert file.is_regular_file("/var/www/.gitignore")


@pytest.mark.setting_ids(["GL-SET-base-config-www-gitignore"])
@pytest.mark.feature("base")
def test_base_www_gitignore_contains_defaults(parse_file: ParseFile):
    """Test that /var/www/.gitignore contains defaults"""
    lines = parse_file.lines("/var/www/.gitignore")
    assert lines == [
        "#nothing",
        "# Ignore everything in this directory",
        "*",
        "# Except this file",
        "!.gitignore",
    ]
