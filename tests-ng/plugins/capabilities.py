from pyprctl import FileCaps
import pytest
from .shell import ShellRunner
from .find import Find, FIND_RESULT_TYPE_FILE


class Capabilities:
    def __init__(self, find: Find, shell: ShellRunner):
        self._find = find
        self._shell = shell

    def list(self) -> list[str]:
        capabilities = []

        self._find.same_mnt_only = False
        self._find.root_path = "/"
        self._find.entry_type = FIND_RESULT_TYPE_FILE

        for f in self._find:
            print(f)
            c = self._shell(f"/usr/sbin/getcap {f}", capture_output=True).stdout.strip()

            if c:
                capabilities.append(c)

        return capabilities

@pytest.fixture
def capabilities(find: Find, shell: ShellRunner) -> Capabilities:
    return Capabilities(find, shell)
