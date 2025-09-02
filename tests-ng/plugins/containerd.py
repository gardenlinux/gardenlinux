import pytest
import validators
from .shell import ShellRunner
from .systemd import Systemd


class CtrRunner:
    def __init__(self, shell: ShellRunner, systemd: Systemd):
        self.shell = shell
        systemd.start_unit("containerd")

    def pull(self, uri):
        validators.url(uri)
        command = f"ctr image pull {uri}"
        self.shell(command, capture_output=False)

    def run(self, uri, container_name, cmd, capture_output=False, ignore_exit_code=False):
        validators.url(uri)
        command = f"ctr run --rm {uri} {container_name} {cmd}"
        return self.shell(command, capture_output=capture_output, ignore_exit_code=ignore_exit_code)


@pytest.fixture
def ctr(shell: ShellRunner, systemd: Systemd):
    return CtrRunner(shell, systemd)
