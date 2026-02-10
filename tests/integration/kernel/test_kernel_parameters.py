import pytest
from plugins.file import File
from plugins.sysctl import Sysctl

# =============================================================================
# cloud Feature
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-cloud-config-sysctl-cloud"])
@pytest.mark.feature("cloud")
def test_cloud_sysctl_cloud_config_exists(file: File):
    """Test that cloud sysctl cloud configuration exists"""
    assert file.exists("/etc/sysctl.d/20-cloud.conf")


@pytest.mark.setting_ids(
    [
        "GL-SET-cloud-config-sysctl-cloud",
        "GL-SET-openstackbaremetal-config-sysctl-cloud",
    ]
)
@pytest.mark.feature("cloud or openstackbaremetal")
@pytest.mark.booted(reason="sysctl needs a booted system")
def test_kernel_parameters_cannot_hardlink_what_you_do_not_own(sysctl):
    assert sysctl["fs.protected_hardlinks"] == 1


@pytest.mark.setting_ids(
    [
        "GL-SET-cloud-config-sysctl-cloud",
        "GL-SET-openstackbaremetal-config-sysctl-cloud",
    ]
)
@pytest.mark.feature("cloud or openstackbaremetal")
@pytest.mark.booted(reason="sysctl needs a booted system")
def test_kernel_parameters_cannot_symlink_what_you_do_not_own(sysctl):
    assert sysctl["fs.protected_symlinks"] == 1


@pytest.mark.setting_ids(
    [
        "GL-SET-cloud-config-sysctl-cloud",
        "GL-SET-openstackbaremetal-config-sysctl-cloud",
    ]
)
@pytest.mark.feature("cloud or openstackbaremetal")
@pytest.mark.booted(reason="sysctl needs a booted system")
def test_kernel_parameters_randomize_memory_allocation(sysctl):
    assert sysctl["kernel.randomize_va_space"] == 2


@pytest.mark.setting_ids(
    "GL-SET-gardener-config-sysctl-gce-network-security",
)
@pytest.mark.feature("gardener")
@pytest.mark.booted(reason="sysctl needs a booted system")
def test_sysctl_rp_filter(sysctl):
    assert sysctl["net.ipv4.conf.all.rp_filter"] != 1
    assert sysctl["net.ipv4.conf.default.rp_filter"] != 1


@pytest.mark.setting_ids(
    [
        "GL-SET-cloud-config-sysctl-ipv4",
        "GL-SET-cloud-config-sysctl-ipv6",
    ]
)
@pytest.mark.feature("cloud")
def test_cloud_sysctl_network_configs_exist(file: File):
    """Test that cloud sysctl network configurations exist"""
    configs = [
        "/etc/sysctl.d/21-ipv4-settings.conf",
        "/etc/sysctl.d/22-ipv6-settings.conf",
    ]
    missing = [cfg for cfg in configs if not file.is_regular_file(cfg)]
    assert not missing, f"Missing cloud sysctl configs: {', '.join(missing)}"


@pytest.mark.setting_ids(
    [
        "GL-SET-cloud-config-sysctl-ipv4",
    ]
)
@pytest.mark.feature("cloud")
def test_cloud_sysctl_network_config_ipv4(sysctl):
    """Test that cloud sysctl network config ipv4 is set correctly"""
    assert sysctl["net.ipv4.tcp_syncookies"] == 1
    assert (
        sysctl["net.ipv4.conf.all.accept_source_route"] == 0
    ), "Cloud sysctl network config ipv4 should have accept source route set to 0"
    assert sysctl["net.ipv4.conf.all.accept_redirects"] == 0
    assert sysctl["net.ipv4.conf.all.secure_redirects"] == 1
    assert sysctl["net.ipv4.conf.default.secure_redirects"] == 1
    assert sysctl["net.ipv4.icmp_echo_ignore_broadcasts"] == 1
    assert sysctl["net.ipv4.icmp_ignore_bogus_error_responses"] == 1
    assert sysctl["net.ipv4.conf.default.accept_source_route"] == 1
    assert sysctl["net.ipv4.conf.default.accept_redirects"] == 1
    assert sysctl["net.ipv4.conf.all.log_martians"] == 0
    assert sysctl["net.ipv4.conf.all.forwarding"] == 1
    assert sysctl["net.ipv4.conf.default.forwarding"] == 1
    assert sysctl["net.ipv4.conf.default.send_redirects"] == 1
    assert sysctl["net.ipv4.conf.all.send_redirects"] == 1
    assert sysctl["net.ipv4.conf.all.promote_secondaries"] == 1


@pytest.mark.setting_ids(
    [
        "GL-SET-cloud-config-sysctl-ipv6",
    ]
)
@pytest.mark.feature("cloud")
def test_cloud_sysctl_network_config_ipv6(sysctl):
    """Test that cloud sysctl network config ipv6 is set correctly"""
    assert sysctl["net.ipv6.conf.all.forwarding"] == 1
    assert sysctl["net.ipv6.conf.default.forwarding"] == 1


# =============================================================================
# chost Feature - Container Networking Sysctl Configuration
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-chost-config-sysctl-ip-forward",
        "GL-SET-chost-config-sysctl-nf-call-iptables",
    ]
)
@pytest.mark.feature("chost")
def test_chost_sysctl_configs_exist(file: File):
    """Test that container networking sysctl configs exist"""
    sysctl_configs = [
        "/etc/sysctl.d/ip-forward.conf",
        "/etc/sysctl.d/nf-call-iptables.conf",
    ]
    missing = [cfg for cfg in sysctl_configs if not file.exists(cfg)]
    assert not missing, f"Missing sysctl configs: {', '.join(missing)}"


@pytest.mark.setting_ids(
    [
        "GL-SET-chost-config-sysctl-ip-forward",
        "GL-SET-chost-config-sysctl-nf-call-iptables",
    ]
)
@pytest.mark.feature("chost")
def test_chost_sysctl_config_content(sysctl: Sysctl):
    """Test that container networking sysctl config contains the correct content"""
    assert sysctl["net.ipv4.ip_forward"] == 1, "IP forwarding should be enabled"
    assert (
        sysctl["net.ipv6.conf.all.forwarding"] == 1
    ), "IP forwarding should be enabled"
    assert sysctl["net.netfilter.nf_call_iptables"] == 1, "iptables should be called"
    assert sysctl["net.netfilter.nf_call_ip6tables"] == 1, "ip6tables should be called"


# =============================================================================
# khost Feature - Kubernetes Host Configuration
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-khost-config-sysctl-br-nf",
        "GL-SET-khost-config-sysctl-inotify",
        "GL-SET-khost-config-sysctl-ip-forward",
    ]
)
@pytest.mark.feature("khost")
def test_khost_sysctl_configs_exist(file: File):
    """Test that Kubernetes host sysctl configs exist"""
    sysctl_configs = [
        "/etc/sysctl.d/20-br-nf.conf",
        "/etc/sysctl.d/20-inotify.conf",
        "/etc/sysctl.d/20-ip-forward.conf",
    ]
    missing = [cfg for cfg in sysctl_configs if not file.exists(cfg)]
    assert not missing, f"Missing khost sysctl configs: {', '.join(missing)}"


@pytest.mark.setting_ids(
    [
        "GL-SET-khost-config-sysctl-br-nf",
        "GL-SET-khost-config-sysctl-inotify",
        "GL-SET-khost-config-sysctl-ip-forward",
    ]
)
@pytest.mark.feature("khost")
def test_khost_sysctl_configs_content(sysctl: Sysctl):
    """Test that Kubernetes host sysctl configs contain the correct content"""
    assert (
        sysctl["net.bridge.bridge-nf-call-iptables"] == 1
    ), "iptables should be called"
    assert (
        sysctl["net.bridge.bridge-nf-call-ip6tables"] == 1
    ), "ip6tables should be called"
    assert (
        sysctl["fs.inotify.max_user_instances"] == 8192
    ), "inotify max user watches should be 1048576"
    assert (
        sysctl["fs.inotify.max_user_watches"] == 65536
    ), "inotify max user watches should be 1048576"
    assert sysctl["net.ipv4.ip_forward"] == 1, "IP forwarding should be enabled"
    assert (
        sysctl["net.ipv6.conf.all.forwarding"] == 1
    ), "IP forwarding should be enabled"


# =============================================================================
# server Feature
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-sysctl-allow-ping-for-non-root-user",
    ]
)
@pytest.mark.feature("server")
def test_server_sysctl_allow_ping_nonroot(file: File):
    """Test that server allows ping for non-root users"""
    assert file.exists(
        "/etc/sysctl.d/90-allow-ping-for-non-root-user.conf"
    ), "Sysctl config for non-root ping should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-sysctl-allow-ping-for-non-root-user",
    ]
)
@pytest.mark.feature("server")
def test_server_sysctl_allow_ping_nonroot_check(sysctl: Sysctl):
    """Test that server sysctl allows ping for non-root users"""
    assert (
        sysctl["net.ipv4.ping_group_range"] == "0 2147483647"
    ), "Ping group range should be '0 2147483647'"


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-sysctl-enable-unprivileged-user-namespaces",
    ]
)
@pytest.mark.feature("server")
def test_server_sysctl_unprivileged_namespaces(file: File):
    """Test that server enables unprivileged user namespaces"""
    assert file.exists(
        "/etc/sysctl.d/40-enable-unprivileged-user-namespaces.conf"
    ), "Sysctl config for unprivileged namespaces should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-sysctl-enable-unprivileged-user-namespaces",
    ]
)
@pytest.mark.feature("server")
def test_server_sysctl_unprivileged_namespaces_check(sysctl: Sysctl):
    """Test that server sysctl allows ping for non-root users"""
    assert (
        sysctl["kernel.unprivileged_userns_clone"] == 1
    ), "Unprivileged namespaces should be enabled"
