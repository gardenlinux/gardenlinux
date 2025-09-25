import pytest
from plugins.containerd import CtrRunner
from handlers.containerd import containerd

TEST_IMAGES = [
    "docker.io/library/busybox:latest",  # Docker Hub, https://hub.docker.com/_/busybox
    "public.ecr.aws/docker/library/busybox:unstable-uclibc",  # AWS ECR, https://gallery.ecr.aws/docker/library/busybox
]


@pytest.mark.skip(
    reason="Skip until https://github.com/gardenlinux/gardenlinux/issues/3567 is resolved to avoid false negative results"
)
@pytest.mark.booted(reason="Container tests require systemd")
@pytest.mark.root(reason="Needs to start containerd")
@pytest.mark.feature(
    "(gardener or chost or _debug) and not _pxe",
    reason="containerd is not installed, pxe has tmpfs for /",
)
@pytest.mark.parametrize("uri", TEST_IMAGES)
def test_basic_container_functionality(containerd, container_image_setup, uri: str, ctr: CtrRunner):
    out = ctr.run(uri, "uname", capture_output=True, ignore_exit_code=True)
    assert "Linux" in out.stdout, f"Command failed: {out.stderr}"
