import pytest
from pyprctl import FileCaps

from .find import FIND_RESULT_TYPE_FILE, Find
from .shell import ShellRunner


class Capabilities:
    def __init__(self, find: Find, shell: ShellRunner):
        self._find = find
        self._shell = shell

    def list(self) -> list[str]:
        capabilities = []

        self._find.same_mnt_only = False
        self._find.root_paths = ["/boot", "/etc", "/usr", "/var"]
        self._find.entry_type = FIND_RESULT_TYPE_FILE

        for file in self._find:
            capability = self._shell(
                f"/usr/sbin/getcap {file}", capture_output=True
            ).stdout.strip()

            if capability:
                capabilities.append(capability)

        return capabilities


@pytest.fixture
def capabilities(find: Find, shell: ShellRunner) -> Capabilities:
    return Capabilities(find, shell)
