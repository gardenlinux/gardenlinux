import pytest
from plugins.containerd import CtrRunner

TEST_IMAGES = [
    "ghcr.io/gardenlinux/gardenlinux:latest", # Github Container Registry, https://github.com/orgs/gardenlinux/packages?ecosystem=container
    "docker.io/library/debian:latest",        # Docker Hub, https://hub.docker.com/_/debian
    "public.ecr.aws/debian/debian:latest",    # AWS ECR, https://gallery.ecr.aws/debian/debian
]


@pytest.mark.feature("server") # server installs systemd and azure has notoriously bad startup times
@pytest.mark.parametrize("uri", TEST_IMAGES)
def test_basic_container_functionality(uri: str, ctr: CtrRunner):
    ctr.pull(uri)

    out = ctr.run(uri, "uname", capture_output=True, ignore_exit_code=True)

    assert "Linux" in out.stdout, f"Command failed: {out.stderr}"
