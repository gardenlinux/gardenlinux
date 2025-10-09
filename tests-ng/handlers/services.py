import pytest
from plugins.systemd import Systemd
from plugins.kernel_module import KernelModule
import time


# generic services
def handle_service(systemd: Systemd, service_name: str):
    """Generic handler for regular systemd services."""
    service_active_initially = systemd.is_active(service_name)

    if not service_active_initially:
        systemd.start_unit(service_name)

    yield service_name

    if not service_active_initially:
        systemd.stop_unit(service_name)


@pytest.fixture
def service_parametrize(
    systemd: Systemd, kernel_module: KernelModule, service_name: str
):
    """
    Generic fixture to manage any systemd unit lifecycle.

    Usage with parametrize:
        @pytest.mark.parametrize("service_name", ["ssh"])
        def test_something(systemd: Systemd, service_parametrize):
            pass
    """
    match service_name:
        case "containerd":
            yield from handle_service_containerd(systemd, kernel_module)
        case _:
            yield from handle_service(systemd, service_name)


# Individual service fixtures (convenience fixtures)
@pytest.fixture
def service_ssh(systemd: Systemd):
    """Fixture for SSH service management."""
    yield from handle_service(systemd, "ssh")


@pytest.fixture
def service_kubelet(systemd: Systemd):
    """Fixture for Kubelet service management."""
    yield from handle_service(systemd, "kubelet")


@pytest.fixture
def service_nftables(systemd: Systemd):
    """Fixture for nftables service management."""
    yield from handle_service(systemd, "nftables")


@pytest.fixture
def service_libvirtd(systemd: Systemd):
    """Fixture for libvirtd service management."""
    yield from handle_service(systemd, "libvirtd")


# custom services
def handle_service_containerd(systemd: Systemd, kernel_module: KernelModule):
    """
    Function to manage containerd systemd unit lifecycle.
    """
    service_name = "containerd"
    service_active_initially = systemd.is_active(service_name)
    overlay_loaded_initially = kernel_module.is_module_loaded("overlay")

    if not service_active_initially:
        systemd.start_unit(service_name)

    yield service_name

    if not service_active_initially:
        systemd.stop_unit(service_name)
        # unmounting "run-containerd-io.containerd.runtime.v2..*" takes a few seconds
        time.sleep(5)

    # the overlay module is not unloaded when stopping containerd, so we need to unload it manually
    if not overlay_loaded_initially:
        kernel_module.unload_module("overlay")


@pytest.fixture
def service_containerd(systemd: Systemd, kernel_module: KernelModule):
    """Fixture for containerd service management."""
    yield from handle_service_containerd(systemd, kernel_module)
