import pytest
from plugins.systemd import Systemd
from handlers.services import service_parametrize
from plugins.kernel_module import KernelModule

FEATURE_SERVICE_MAPPING = [
    {
        "feature": "khost",
        "service": "kubelet"
    },
    {
        "feature": "firewall",
        "service": "nftables"
    },
    {
        "feature": "gardener",
        "service": "containerd"
    },
    {
        "feature": "vhost",
        "service": "libvirtd"
    }
]


@pytest.mark.parametrize(
    "feature,service_name",
    [pytest.param(mapping["feature"], mapping["service"], marks=pytest.mark.feature(mapping["feature"])) for mapping in FEATURE_SERVICE_MAPPING]
)
@pytest.mark.booted(reason="Test runs systemd")
@pytest.mark.root(reason="To start the systemd service")
@pytest.mark.modify(reason="Starts systemd service")
def test_systemd_unit(systemd: Systemd, kernel_module: KernelModule, service_parametrize, feature):
    # The service fixture will handle starting/stopping the service
    # Verify the service is active (the service fixture will have started it if needed)
    assert systemd.is_active(service_parametrize), f"Required service {service_parametrize} for {feature} feature is not running"
