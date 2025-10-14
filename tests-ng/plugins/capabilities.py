import pytest
from .shell import ShellRunner

class Capabilities:
    def __init__(self, shell: ShellRunner):
        self._shell = shell

    def list(self) -> list[str]:
        return self._shell("find /boot /etc /usr /var -type f -exec /usr/sbin/getcap {} \\;", capture_output=True).stdout.splitlines()

@pytest.fixture
def capabilities(shell: ShellRunner) -> Capabilities:
    return Capabilities(shell)
