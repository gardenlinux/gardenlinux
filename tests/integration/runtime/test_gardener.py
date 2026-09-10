import pytest
from plugins.file import File
from plugins.modify import allow_system_modifications
from plugins.parse_file import ParseFile
from plugins.systemd import Systemd

# =============================================================================
# gardener Feature - Gardener Kubernetes Extended
# =============================================================================


@pytest.mark.testcov(
    [
        "GL-TESTCOV-gardener-config-containerd-no-config",
    ]
)
@pytest.mark.feature("gardener")
def test_gardener_no_containerd_default_config(file: File):
    """Test that gardener does not have default containerd config"""
    assert not file.exists(
        "/etc/containerd/config.toml"
    ), "Gardener should not have default containerd config"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-gardener-config-iptables-legacy",
    ]
)
@pytest.mark.feature("gardener")
def test_gardener_iptables_legacy_alternative(file: File):
    """Test that gardener has iptables legacy alternative configured"""
    symlinks = [
        {"path": "/etc/alternatives/iptables", "target": "/usr/sbin/iptables-legacy"},
        {"path": "/etc/alternatives/ip6tables", "target": "/usr/sbin/ip6tables-legacy"},
        {"path": "/etc/alternatives/arptables", "target": "/usr/sbin/arptables-legacy"},
        {"path": "/etc/alternatives/ebtables", "target": "/usr/sbin/ebtables-legacy"},
    ]
    missing = [
        symlink
        for symlink in symlinks
        if not file.is_symlink(symlink["path"], symlink["target"])
    ]
    assert (
        not missing
    ), f"Gardener iptables alternatives should be symlinks to iptables-legacy, but are {missing}: {', '.join([symlink['path'] for symlink in missing])}"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-gardener-config-security-mount-no-sbit",
    ]
)
@pytest.mark.feature("gardener")
def test_gardener_mount_no_sbit_security(file: File):
    """Test that gardener has mount security without sbit"""
    files = [
        "/sbin/mount.nfs",
        "/sbin/mount.cifs",
    ]
    missing = [file_path for file_path in files if not file.has_mode(file_path, "0755")]
    assert (
        not missing
    ), f"Gardener mount security should be without sbit, but are {missing}: {', '.join([file_path for file_path in missing])}"


# =============================================================================
# gardener Feature Services
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-gardener-service-apparmor-enable"])
@pytest.mark.feature("gardener")
@pytest.mark.booted(reason="Requires systemd")
def test_gardener_apparmor_service_enabled(systemd: Systemd):
    """Test that apparmor.service is enabled"""
    assert systemd.is_enabled("apparmor.service")


@pytest.mark.testcov(["GL-TESTCOV-gardener-service-apparmor-enable"])
@pytest.mark.feature("gardener")
@pytest.mark.booted(reason="Requires systemd")
def test_gardener_apparmor_service_active(systemd: Systemd):
    """Test that apparmor.service is active"""
    assert systemd.is_active("apparmor.service")


@pytest.mark.testcov(
    [
        "GL-TESTCOV-gardener-service-containerd-enable",
        "GL-TESTCOV-gardener-service-containerd-disable",
    ]
)
@pytest.mark.feature("gardener")
@pytest.mark.booted(reason="Requires systemd")
def test_gardener_containerd_service_disabled(systemd: Systemd):
    """Test that containerd.service is disabled"""
    assert systemd.is_disabled("containerd.service")


@pytest.mark.testcov(
    [
        "GL-TESTCOV-gardener-service-containerd-enable",
        "GL-TESTCOV-gardener-service-containerd-disable",
    ]
)
@pytest.mark.feature("gardener")
@pytest.mark.booted(reason="Requires systemd")
def test_gardener_containerd_service_inactive(systemd: Systemd):
    """Test that containerd.service is inactive"""
    assert systemd.is_inactive("containerd.service")


@pytest.mark.testcov(["GL-TESTCOV-gardener-service-logrotate-enable"])
@pytest.mark.feature("gardener")
@pytest.mark.booted(reason="Requires systemd")
def test_gardener_logrotate_timer_service_enabled(systemd: Systemd):
    """Test that logrotate.timer is enabled"""
    assert systemd.is_enabled("logrotate.timer")


@pytest.mark.testcov(["GL-TESTCOV-gardener-service-logrotate-enable"])
@pytest.mark.feature("gardener")
@pytest.mark.booted(reason="Requires systemd")
def test_gardener_logrotate_timer_service_active(systemd: Systemd):
    """Test that logrotate.timer is active"""
    assert systemd.is_active("logrotate.timer")


@pytest.mark.testcov(["GL-TESTCOV-gardener-service-ssh-disable"])
@pytest.mark.feature("gardener")
@pytest.mark.booted(reason="Requires systemd")
def test_gardener_ssh_service_disabled(systemd: Systemd):
    """Test that ssh.service is disabled"""
    # TODO: find better way to exclude this
    if allow_system_modifications():
        pytest.skip("ssh.service is enabled to connect to test instances")
    else:
        assert systemd.is_disabled("ssh.service")


@pytest.mark.testcov(["GL-TESTCOV-gardener-service-ssh-disable"])
@pytest.mark.feature("gardener")
@pytest.mark.booted(reason="Requires systemd")
def test_gardener_ssh_service_inactive(systemd: Systemd):
    """Test that ssh.service is inactive"""
    # TODO: find better way to exclude this
    if allow_system_modifications():
        pytest.skip("ssh.service is enabled to connect to test instances")
    else:
        assert systemd.is_inactive("ssh.service")


@pytest.mark.testcov(
    [
        "GL-TESTCOV-gardener-config-containerd-override",
    ]
)
@pytest.mark.feature("gardener")
def test_gardener_containerd_override_exists(file: File):
    """Test that gardener containerd service override exists"""
    assert file.exists(
        "/etc/systemd/system/containerd.service.d/override.conf"
    ), "Gardener containerd service override should exist"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-gardener-config-containerd-override",
    ]
)
@pytest.mark.feature("gardener")
def test_gardener_containerd_override_content(parse_file: ParseFile):
    """Test that gardener containerd service override contains the correct content"""
    config = parse_file.parse(
        "/etc/systemd/system/containerd.service.d/override.conf", format="ini"
    )
    assert (
        config["Service"]["LimitMEMLOCK"] == "67108864"
    ), "Gardener containerd service override should include correct LimitMEMLOCK value"
    assert (
        config["Service"]["LimitNOFILE"] == "1048576"
    ), "Gardener containerd service override should include correct LimitNOFILE value"


@pytest.mark.testcov(["GL-TESTCOV-gardener-service-containerd-disable"])
@pytest.mark.booted(reason="Test runs systemd")
@pytest.mark.root(reason="To start the systemd service")
@pytest.mark.modify(reason="Starts systemd service")
@pytest.mark.feature("gardener or chost")
def test_gardener_containerd_can_be_started(systemd: Systemd, service_containerd):
    """Test that containerd.service can be started. It will be started and stopped by the service fixture."""
    assert systemd.is_active(
        "containerd.service"
    ), "containerd.service is still running"
