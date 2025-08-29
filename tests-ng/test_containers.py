import pytest
from plugins.shell import ShellRunner

TEST_IMAGES = [
    "ghcr.io/gardenlinux/gardenlinux:1592.12",    # Github Container Registry, https://github.com/orgs/gardenlinux/packages?ecosystem=container
    "docker.io/library/debian:12.11-slim",        # Docker Hub, https://hub.docker.com/_/debian
    "public.ecr.aws/debian/debian:11",            # AWS ECR, https://gallery.ecr.aws/debian/debian
]


@pytest.fixture
def containerd(shell: ShellRunner):
    shell("systemctl start containerd", capture_output=False)
    yield
    shell("systemctl stop containerd", capture_output=False)


def test_basic_container_functionality(shell: ShellRunner, containerd):
    for uri in TEST_IMAGES:
        pull_command = f"ctr image pull {uri}"
        shell(pull_command, capture_output=False)

        container_name = uri.split("/")[0].replace(".", "-")
        command = f"ctr run --rm {uri} {container_name} uname"
        out = shell(command, capture_output=True, ignore_exit_code=True)

        assert "Linux" in out.stdout, "Command {} failed: {}".format(command, out.stderr)
