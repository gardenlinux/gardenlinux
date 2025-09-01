import pytest
from plugins.containerd import CtrRunner

TEST_IMAGES = [
    "ghcr.io/gardenlinux/gardenlinux:latest", # Github Container Registry, https://github.com/orgs/gardenlinux/packages?ecosystem=container
    "docker.io/library/debian:latest",        # Docker Hub, https://hub.docker.com/_/debian
    "public.ecr.aws/debian/debian:latest",    # AWS ECR, https://gallery.ecr.aws/debian/debian
]


def test_basic_container_functionality(ctr: CtrRunner):
    for uri in TEST_IMAGES:
        ctr.pull(uri)

        container_name = uri.split("/")[0].replace(".", "-")
        out = ctr.run(uri, container_name, "uname", capture_output=True, ignore_exit_code=True)

        assert "Linux" in out.stdout, f"Command failed: {out.stderr}"
