import pytest
from plugins.file import File

# =============================================================================
# gardener Feature - Gardener Kubernetes Extended
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-gardener-config-containerd-no-config",
    ]
)
@pytest.mark.feature("gardener")
def test_gardener_no_containerd_default_config(file: File):
    """Test that gardener does not have default containerd config"""
    assert not file.exists(
        "/etc/containerd/config.toml"
    ), "Gardener should not have default containerd config"


@pytest.mark.setting_ids(
    [
        "GL-SET-gardener-config-iptables-legacy",
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


@pytest.mark.setting_ids(
    [
        "GL-SET-gardener-config-security-mount-no-sbit",
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
