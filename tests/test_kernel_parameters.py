import pytest
from plugins.file import File
from plugins.sysctl import Sysctl


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


@pytest.mark.booted
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
