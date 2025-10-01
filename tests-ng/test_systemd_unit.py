import pytest
from plugins.systemd import Systemd


# The key is the feature condition of the test which checks if the systemd unit (value) is working
units = {
    "chost or khost": "kubelet",
    "firewall": "nftables",
    "gardener": "containerd",
    "vhost": "libvirtd"
}


@pytest.mark.parametrize(
    "systemd_unit,feature", [pytest.param(units[feature], feature, marks=pytest.mark.feature(feature)) for feature in units]
)
@pytest.mark.booted(reason="Test runs systemd")
@pytest.mark.root(reason="To start the systemd service")
@pytest.mark.modify(reason="Starts systemd service")
def test_systemd_unit(systemd: Systemd, systemd_unit, feature):
    systemd.start_unit(systemd_unit)
    assert systemd.is_active(systemd_unit), f"Required systemd unit {systemd_unit} for {feature} feature is not running"
