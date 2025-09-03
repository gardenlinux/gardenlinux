import pytest
from plugins.containerd import CtrRunner

TEST_IMAGES = [
    "ghcr.io/gardenlinux/gardenlinux:latest", # Github Container Registry, https://github.com/orgs/gardenlinux/packages?ecosystem=container
    "docker.io/library/debian:latest",        # Docker Hub, https://hub.docker.com/_/debian
    "public.ecr.aws/debian/debian:latest",    # AWS ECR, https://gallery.ecr.aws/debian/debian
]


@pytest.fixture
def container_image_setup(uri: str, ctr: CtrRunner):
    ctr.pull_image(uri)
    yield
    ctr.remove_image(uri)


@pytest.mark.booted(reason="Container tests require systemd")
@pytest.mark.parametrize("uri", TEST_IMAGES)
def test_basic_container_functionality(container_image_setup, uri: str, ctr: CtrRunner):
    out = ctr.run(uri, "uname", capture_output=True, ignore_exit_code=True)
    assert "Linux" in out.stdout, f"Command failed: {out.stderr}"
