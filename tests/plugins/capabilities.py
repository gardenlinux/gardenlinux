import pytest
from pyprctl import FileCaps

from .find import FIND_RESULT_TYPE_FILE, Find
from .shell import ShellRunner


class Capabilities:
    def __init__(self, find: Find, shell: ShellRunner):
        self._find = find
        self._shell = shell

    def get(self) -> set[str]:
        capabilities = set()

        self._find.same_mnt_only = True
        self._find.root_paths = ["/boot", "/etc", "/usr", "/var"]
        self._find.entry_type = FIND_RESULT_TYPE_FILE

        for file in self._find:
            try:
                capability = FileCaps.get_for_file(file)
            except OSError:
                # Skip files without capability xattr or unreadable entries
                continue

            if capability:
                # getcap style output
                capabilities.add(f"{file} {str(capability)}")

        return capabilities


@pytest.fixture
def capabilities(find: Find, shell: ShellRunner) -> Capabilities:
    return Capabilities(find, shell)
