import pytest
from plugins.containerd import CtrRunner

TEST_IMAGES = [
    "docker.io/library/busybox:latest",                       # Docker Hub, https://hub.docker.com/_/busybox
    "public.ecr.aws/docker/library/busybox:unstable-uclibc",  # AWS ECR, https://gallery.ecr.aws/docker/library/busybox
]

@pytest.mark.booted(reason="Container tests require systemd")
@pytest.mark.root(reason="Needs to start containerd")
@pytest.mark.feature("gardener or chost or _debug", reason="containerd is not installed")
@pytest.mark.parametrize("uri", TEST_IMAGES)
def test_basic_container_functionality(container_image_setup, uri: str, ctr: CtrRunner):
    out = ctr.run(uri, "uname", capture_output=True, ignore_exit_code=True)
    assert "Linux" in out.stdout, f"Command failed: {out.stderr}"
