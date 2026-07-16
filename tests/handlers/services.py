import time

import pytest
from plugins.kernel_module import KernelModule
from plugins.systemd import Systemd


# generic services
def handle_service(systemd: Systemd, service_name: str):
    """Generic handler for regular systemd services."""
    service_active_initially = systemd.is_active(service_name)

    if not service_active_initially:
        systemd.start_unit(service_name)

    yield service_name

    if not service_active_initially:
        systemd.stop_unit(service_name)


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


def handle_service_ssh(systemd: Systemd):
    """
    Function to manage ssh systemd unit lifecycle.
    """
    service_name = "ssh"
    service_active_initially = systemd.is_active(service_name)

    if not service_active_initially:
        systemd.start_unit(service_name)

    yield service_name

    if not service_active_initially:
        systemd.stop_unit(service_name)


# Fixtures
@pytest.fixture
def service_containerd(systemd: Systemd, kernel_module: KernelModule):
    """Fixture for containerd service management."""
    yield from handle_service_containerd(systemd, kernel_module)


@pytest.fixture
def service_ssh(systemd: Systemd):
    """Fixture for ssh service management."""
    yield from handle_service(systemd, "ssh")
