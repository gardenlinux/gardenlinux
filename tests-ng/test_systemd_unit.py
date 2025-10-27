import pytest
from handlers.services import service_parametrize
from plugins.kernel_module import KernelModule
from plugins.systemd import Systemd

FEATURE_SERVICE_MAPPING = [
    # TODO: This service is enabled and starts at boot time. So starting/stopping it does not make sense. Currently it fails with this error message:
    # Oct 13 06:59:25 localhost (kubelet)[758]: kubelet.service: Referenced but unset environment variable evaluates to an empty string: KUBELET_KUBEADM_ARGS
    # Oct 13 06:59:30 localhost kubelet[758]: E1013 06:59:30.007483     758 run.go:74] "command failed" err="failed to load kubelet config file, path: /var/lib/kubelet/config.yaml, error: failed to load Kubelet config file /var/lib/kubelet/config.yaml, error failed to read kubelet config file \"/var/lib/kubelet/config.yaml\", error: open /var/lib/kubelet/config.yaml: no such file or directory"
    # {
    #     "feature": "khost",
    #     "service": "kubelet"
    # },
    # TODO: This service is enabled and starts at boot time. So starting/stopping it does not make sense.
    {"feature": "firewall", "service": "nftables"},
    # This service is disabled at boot time and is started/stopped here.
    {"feature": "gardener", "service": "containerd"},
    # TODO: This service is enabled and starts at boot time. So starting/stopping it does not make sense.
    {"feature": "vhost", "service": "libvirtd"},
]


@pytest.mark.parametrize(
    "feature,service_name",
    [
        pytest.param(
            mapping["feature"],
            mapping["service"],
            marks=pytest.mark.feature(mapping["feature"]),
        )
        for mapping in FEATURE_SERVICE_MAPPING
    ],
)
@pytest.mark.booted(reason="Test runs systemd")
@pytest.mark.root(reason="To start the systemd service")
@pytest.mark.modify(reason="Starts systemd service")
def test_systemd_unit(
    systemd: Systemd, kernel_module: KernelModule, service_parametrize, feature
):
    # The service fixture will handle starting/stopping the service
    # Verify the service is active (the service fixture will have started it if needed)
    assert systemd.is_active(
        service_parametrize
    ), f"Required service {service_parametrize} for {feature} feature is not running"
