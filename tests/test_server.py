import pytest
from plugins.file import File
from plugins.parse_file import ParseFile
from plugins.systemd import Systemd

# =============================================================================
# server Feature - MOTD Scripts
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-update-motd-hostname",
        "GL-SET-server-config-update-motd-line-001",
        "GL-SET-server-config-update-motd-uname",
        "GL-SET-server-config-update-motd-load",
        "GL-SET-server-config-update-motd-free",
        "GL-SET-server-config-update-motd-network",
        "GL-SET-server-config-update-motd-line-002",
        "GL-SET-server-config-update-motd-logo",
        "GL-SET-server-config-update-motd-needrestart",
        "GL-SET-server-config-update-motd-unattended-upgrades",
    ]
)
@pytest.mark.feature("server")
def test_server_motd_scripts_exist(file: File):
    """Test that MOTD scripts exist"""
    motd_scripts = [
        "/etc/update-motd.d/05-logo",
        "/etc/update-motd.d/10-hostname",
        "/etc/update-motd.d/20-uname",
        "/etc/update-motd.d/30-load",
        "/etc/update-motd.d/40-free",
        "/etc/update-motd.d/45-line",
        "/etc/update-motd.d/50-network",
        "/etc/update-motd.d/55-line",
        "/etc/update-motd.d/92-unattended-upgrades",
        "/etc/update-motd.d/95-needrestart",
    ]

    missing = [script for script in motd_scripts if not file.exists(script)]
    assert not missing, f"Missing MOTD scripts: {', '.join(missing)}"


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-update-motd-hostname",
        "GL-SET-server-config-update-motd-line-001",
        "GL-SET-server-config-update-motd-uname",
        "GL-SET-server-config-update-motd-load",
        "GL-SET-server-config-update-motd-free",
        "GL-SET-server-config-update-motd-network",
        "GL-SET-server-config-update-motd-line-002",
        "GL-SET-server-config-update-motd-logo",
        "GL-SET-server-config-update-motd-needrestart",
        "GL-SET-server-config-update-motd-unattended-upgrades",
    ]
)
@pytest.mark.feature("server")
def test_server_motd_scripts_content(parse_file: ParseFile):
    """Test that MOTD contains the correct content"""
    lines = parse_file.lines("/etc/motd")
    assert "Garden Linux" in lines, "Garden Linux should be in /etc/motd"
    assert (
        "based on Debian GNU/Linux forky" in lines
    ), "based on Debian GNU/Linux forky should be in /etc/motd"
    assert "Welcome to" in lines, "Welcome to should be in /etc/motd"


# =============================================================================
# server Feature - Filesystem overrides
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-service-systemd-growfs-override",
    ]
)
@pytest.mark.feature("server")
def test_server_systemd_growfs_override_exists(file: File):
    """Test that systemd-growfs service override exists"""
    # The growfs service might be in different paths
    paths = [
        "/etc/systemd/system/systemd-growfs@.service.d/override.conf",
        "/etc/systemd/system/systemd-growfs-root.service.d/override.conf",
    ]
    exists = any(file.exists(path) for path in paths)
    assert exists, f"systemd-growfs override not found in any of: {', '.join(paths)}"


# =============================================================================
# server Feature - Network & Resolved Configuration
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-service-systemd-networkd-wait-online-any",
    ]
)
@pytest.mark.feature("server")
def test_server_systemd_networkd_wait_online_override_exists(file: File):
    """Test that systemd-networkd-wait-online service override exists"""
    assert file.exists(
        "/etc/systemd/system/systemd-networkd-wait-online.service.d/override.conf"
    )


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-service-systemd-resolved-wait-for-networkd",
    ]
)
@pytest.mark.feature("server")
def test_server_systemd_resolved_networkd_dependency_exists(file: File):
    """Test that systemd-resolved has networkd dependency override"""
    assert file.exists(
        "/etc/systemd/system/systemd-resolved.service.d/wait-for-networkd.conf"
    )


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-resolved-llmnr-disable",
    ]
)
@pytest.mark.feature("server")
def test_server_systemd_resolved_llmn_config_exists(file: File):
    """Test that systemd-resolved LLMNR configuration exists"""
    assert file.exists(
        "/etc/systemd/resolved.conf.d/00-disable-llmnr.conf"
    ), "systemd-resolved LLMNR configuration should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-resolved-llmnr-disable",
    ]
)
@pytest.mark.feature("server")
def test_server_systemd_resolved_llmnr_disabled(parse_file: ParseFile):
    """Test that LLMNR is disabled in systemd-resolved"""

    lines = parse_file.lines("/etc/systemd/resolved.conf.d/00-disable-llmnr.conf")
    assert "LLMNR=no" in lines, "LLMNR should be disabled in systemd-resolved"


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-resolved-mdns-disable",
    ]
)
@pytest.mark.feature("server")
def test_server_systemd_resolved_mdns_config_exists(file: File):
    """Test that systemd-resolved mDNS configuration exists"""
    assert file.exists(
        "/etc/systemd/resolved.conf.d/01-disable-mdns.conf"
    ), "systemd-resolved mDNS configuration should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-resolved-mdns-disable",
    ]
)
@pytest.mark.feature("server")
def test_server_systemd_resolved_mdns_disabled(parse_file: ParseFile):
    """Test that mDNS is disabled in systemd-resolved"""
    lines = parse_file.lines("/etc/systemd/resolved.conf.d/01-disable-mdns.conf")
    assert (
        "MulticastDNS=no" in lines
    ), "MulticastDNS should be disabled in systemd-resolved"


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-network-server",
    ]
)
@pytest.mark.feature("server")
def test_server_systemd_networkd_server_config_exists(parse_file: ParseFile):
    """Test that Foreign Routing is disabled in Networkd configuration"""
    lines = parse_file.lines("/etc/systemd/networkd.conf.d/00-gardenlinux-server.conf")
    assert (
        "ManageForeignRoutingPolicyRules=no" in lines
    ), "Foreign Routing Policy Rules should be disabled in Networkd"
    assert (
        "ManageForeignRoutes=no" in lines
    ), "Foreign Routes should be disabled in Networkd"


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-network-server",
    ]
)
@pytest.mark.feature("server")
def test_server_systemd_networkd_foreign_routing_disabled(parse_file: ParseFile):
    """Test that Foreign Routing is disabled in Networkd configuration"""
    lines = parse_file.lines("/etc/systemd/networkd.conf.d/00-gardenlinux-server.conf")
    assert (
        "ManageForeignRoutingPolicyRules=no" in lines
    ), "Foreign Routing Policy Rules should be disabled in Networkd"
    assert (
        "ManageForeignRoutes=no" in lines
    ), "Foreign Routes should be disabled in Networkd"


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-resolv-conf-link",
    ]
)
@pytest.mark.feature("server")
def test_server_resolv_conf_stub_link(file: File):
    """Test that resolv.conf is a symlink to stub-resolv.conf"""
    assert file.is_symlink(
        "/etc/resolv.conf", "/run/systemd/resolve/resolv.conf"
    ), "/etc/resolv.conf should be a symlink to /run/systemd/resolve/resolv.conf"


# =============================================================================
# server Feature - System Configuration
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-hosts-permissions",
    ]
)
@pytest.mark.feature("server")
def test_server_hosts_file_permissions(file: File):
    """Test that /etc/hosts has correct permissions"""
    assert file.has_mode(
        "/etc/hosts", "0644"
    ), "/etc/hosts should have 0644 permissions"


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-sudoers-wheel",
    ]
)
@pytest.mark.feature("server")
def test_server_sudoers_wheel_exists(file: File):
    """Test that sudoers wheel configuration exists"""
    assert file.exists("/etc/sudoers.d/wheel"), "/etc/sudoers.d/wheel should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-sudoers-wheel",
    ]
)
@pytest.mark.feature("server")
def test_server_sudoers_wheel_content(parse_file: ParseFile):
    """Test that sudoers wheel configuration contains the correct content"""
    lines = parse_file.lines("/etc/sudoers.d/wheel")
    assert (
        "%wheel  ALL=(ALL:ALL) NOPASSWD: ALL" in lines
    ), "sudoers wheel configuration should contain the correct content"


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-sudoers-keepssh",
    ]
)
@pytest.mark.feature("server")
def test_server_sudoers_keepssh_exists(file: File):
    """Test that sudoers keepssh configuration exists"""
    assert file.exists("/etc/sudoers.d/keepssh"), "/etc/sudoers.d/keepssh should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-sudoers-keepssh",
    ]
)
@pytest.mark.feature("server")
def test_server_sudoers_keepssh_content(parse_file: ParseFile):
    """Test that sudoers keepssh configuration contains the correct content"""
    lines = parse_file.lines("/etc/sudoers.d/keepssh")
    assert (
        "Defaults    env_keep+=SSH_AUTH_SOCK" in lines
    ), "sudoers keepssh configuration should contain the correct content"


# =============================================================================
# server Feature - Additional System Files
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-locale-conf",
    ]
)
@pytest.mark.feature("server")
def test_server_locale_conf_exists(file: File):
    """Test that locale.conf exists"""
    assert file.is_regular_file("/etc/locale.conf"), "/etc/locale.conf should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-locale-conf",
    ]
)
@pytest.mark.feature("server")
def test_server_locale_conf_content(parse_file: ParseFile):
    """Test that locale.conf contains the correct content"""
    lines = parse_file.lines("/etc/locale.conf")
    assert "LANG=C.UTF-8" in lines, "LANG should be C.UTF-8"
    assert "LANGUAGE=en_US:en" in lines, "LANGUAGE should be en_US:en"


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-no-init-auditd",
        "GL-SET-server-config-no-init-dbus",
        "GL-SET-server-config-no-init-kexec",
        "GL-SET-server-config-no-init-kexec-load",
        "GL-SET-server-config-no-init-sudo",
        "GL-SET-server-config-no-init-sysstat",
        "GL-SET-server-config-no-init-udev",
    ]
)
@pytest.mark.feature("server")
def test_server_no_init_scripts(file: File):
    """Test that server does not have unnecessary init scripts"""
    init_scripts = [
        "/etc/init.d/auditd",
        "/etc/init.d/dbus",
        "/etc/init.d/kexec",
        "/etc/init.d/kexec-load",
        "/etc/init.d/sudo",
        "/etc/init.d/sysstat",
        "/etc/init.d/udev",
    ]
    existing = [script for script in init_scripts if file.exists(script)]
    assert not existing, f"Unexpected init scripts found: {', '.join(existing)}"


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-no-games",
        "GL-SET-server-config-no-monit",
        "GL-SET-server-config-no-pycache",
    ]
)
@pytest.mark.feature("server")
def test_server_no_unnecessary_dirs(file: File):
    """Test that server does not have unnecessary directories"""
    dirs = [
        "/usr/games",
        "/etc/monit",
        "/usr/lib/python*/__pycache__",  # Pattern
    ]
    missing = [dir for dir in dirs if not file.is_dir(dir)]
    assert not missing, f"Unnecessary directories found: {', '.join(missing)}"


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-no-runit",
        "GL-SET-server-config-no-runit-log",
        "GL-SET-server-config-no-sv",
    ]
)
@pytest.mark.feature("server")
def test_server_no_runit_files(file: File):
    """Test that server does not have runit service manager files"""
    runit_paths = [
        "/etc/runit",
        "/etc/runit/1",
        "/var/log/runit",
        "/etc/sv",
    ]
    existing = [path for path in runit_paths if file.exists(path)]
    assert not existing, f"Unexpected runit files found: {', '.join(existing)}"


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-no-ufw",
    ]
)
@pytest.mark.feature("server")
def test_server_no_ufw(file: File):
    """Test that server does not have UFW firewall"""
    assert not file.exists("/etc/ufw"), "UFW should not be present"


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-no-vmlinuz",
        "GL-SET-server-config-no-vmlinuz-old",
    ]
)
@pytest.mark.feature("server")
def test_server_no_vmlinuz_in_root(file: File):
    """Test that server does not have vmlinuz files in root directory"""
    vmlinuz_files = [
        "/vmlinuz",
        "/vmlinuz.old",
    ]
    existing = [f for f in vmlinuz_files if file.exists(f)]
    assert not existing, f"vmlinuz files should not be in root: {', '.join(existing)}"


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-no-dbus-machine-id",
    ]
)
@pytest.mark.feature("server")
def test_server_no_dbus_machine_id(file: File):
    """Test that server does not have static dbus machine-id"""
    # machine-id should be a symlink to /etc/machine-id, not a static file
    if file.exists("/var/lib/dbus/machine-id"):
        assert file.is_symlink(
            "/var/lib/dbus/machine-id"
        ), "/var/lib/dbus/machine-id should be a symlink, not a static file"


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-no-private-log",
    ]
)
@pytest.mark.feature("server")
def test_server_no_private_log(file: File):
    """Test that server does not have private log directory"""
    assert not file.exists("/var/log/private"), "Private log directory should not exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-mount-tmp",
    ]
)
@pytest.mark.feature("server")
def test_server_mount_tmp_exists(file: File):
    """Test that server has tmp mount configuration"""
    assert file.exists("/etc/systemd/system/tmp.mount")


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-mount-tmp-enable",
    ]
)
@pytest.mark.feature("server")
def test_server_mount_tmp_enabled(systemd: Systemd):
    """Test that server tmp mount is enabled"""
    assert systemd.is_enabled("tmp.mount")


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-mount-tmp-enable",
    ]
)
@pytest.mark.feature("server")
def test_server_mount_tmp_active(systemd: Systemd):
    """Test that server tmp mount is active"""
    assert systemd.is_active("tmp.mount")


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-network-default",
    ]
)
@pytest.mark.feature("server")
def test_server_network_default_config_exists(file: File):
    """Test that server has network default configuration"""
    assert file.exists("/etc/systemd/network/99-default.network")
