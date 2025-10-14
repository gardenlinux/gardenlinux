import pathlib
import pytest
import validators
from .shell import ShellRunner
from .systemd import Systemd
from .container_registry import ContainerRegistry


class CtrRunner:
    """
    Simple wrapper for 'ctr' shell calls.
    Container image uris are validated before use. Expect an exception if a malformed URI is passed.
    """

    def __init__(self, shell: ShellRunner, systemd: Systemd):
        self.shell = shell
        systemd.start_unit("containerd")

    def pull_image(self, uri, capture_output=False, ignore_exit_code=False):
        validators.url(uri)
        command = f"ctr image pull --plain-http --http-trace --http-dump {uri}"
        return self.shell(command, capture_output=capture_output, ignore_exit_code=ignore_exit_code)

    def remove_image(self, uri, capture_output=False, ignore_exit_code=False):
        validators.url(uri)
        command = f"ctr image rm {uri}"
        return self.shell(command, capture_output=capture_output, ignore_exit_code=ignore_exit_code)

    def run(self, uri, cmd, capture_output=False, ignore_exit_code=False):
        validators.url(uri)

        container_name = uri.split("/")[0].split(":")[0].replace(".", "-")
        command = f"ctr run --rm {uri} {container_name} {cmd}"
        return self.shell(command, capture_output=capture_output, ignore_exit_code=ignore_exit_code)


@pytest.fixture
def ctr(shell: ShellRunner, systemd: Systemd):
    return CtrRunner(shell, systemd)


@pytest.fixture
def container_image_setup(uri: str, ctr: CtrRunner, container_registry: ContainerRegistry):
    # capture output to avoid it cluttering the test logs
    # ctr is very verbose when pulling an image
    container_registry.start()
    ctr.pull_image(uri, capture_output=True)
    yield
    container_registry.shutdown()
    ctr.remove_image(uri, capture_output=True)
