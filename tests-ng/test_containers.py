import pytest

from plugins.container_registry import ContainerRegistry
from plugins.containerd import CtrRunner

TEST_IMAGES = ["localhost:5000/busybox:latest"]


@pytest.mark.booted(reason="Container tests require systemd")
@pytest.mark.root(reason="Needs to start containerd")
@pytest.mark.feature(
    "(gardener or chost or _debug) and not _pxe",
    reason="containerd is not installed, pxe has tmpfs for /",
)
@pytest.mark.parametrize("uri", TEST_IMAGES)
def test_basic_container_functionality(
    container_image_setup,
    uri: str,
    ctr: CtrRunner,
    container_registry: ContainerRegistry,
):
    out = ctr.run(uri, "uname", capture_output=True, ignore_exit_code=True)
    assert "Linux" in out.stdout, f"Command failed: {out.stderr}"
