import pytest
from .shell import ShellRunner

class Capabilities:
    def __init__(self, shell: ShellRunner):
        self._shell = shell

    def list(self) -> list[str]:
        output_lines = self._shell("find /boot /etc /usr /var -type f -exec /usr/sbin/getcap {} \\;", capture_output=True).stdout.splitlines()
        return [line for line in output_lines]

@pytest.fixture
def capabilities(shell: ShellRunner) -> Capabilities:
    return Capabilities(shell)
