import pytest
import time

from plugins.systemd import Systemd
from plugins.kernel_module import KernelModule

@pytest.fixture
def containerd(systemd: Systemd, kernel_module: KernelModule):
    containerd_active_initially = systemd.is_active("containerd")
    overlay_loaded_initially = kernel_module.is_module_loaded("overlay")

    if not containerd_active_initially:
        systemd.start_unit("containerd")

    yield

    if not containerd_active_initially:
        systemd.stop_unit("containerd")
        # unmounting "run-containerd-io.containerd.runtime.v2..*" takes a few seconds
        time.sleep(5)

    # the overlay module is not unloaded when stopping containerd, so we need to unload it manually
    if not overlay_loaded_initially:
        kernel_module.unload_module("overlay")
