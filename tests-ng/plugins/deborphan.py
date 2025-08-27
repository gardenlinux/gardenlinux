import pytest
from .shell import ShellRunner

class DebOrphan:
    """
    Defines a wrapper around the deborphan command.
    """
    def __init__(self, shell: ShellRunner):
        self._shell = shell

    def save_manually_installed_packages(self, savefile: str = "/var/lib/deborphan/keep") -> bool:
        result = self._shell(f"DEBIAN_FRONTEND=noninteractive apt-mark showmanual > {savefile}", ignore_exit_code=True)
        if result.returncode != 0:
            print(result.stderr)

        return result.returncode == 0
    
    def find_orphans(self) -> list[str]:
        """
        Find orphaned packages
        """
        result = self._shell("deborphan -an --no-show-section", capture_output=True, ignore_exit_code=True)

        if result.returncode != 0:
            raise ValueError(f"deborphan failed: {result.stderr}")

        # Get orphaned packages
        return list(filter(None, result.stdout.split('\n')))

@pytest.fixture
def deborphan(shell: ShellRunner) -> DebOrphan:
    return DebOrphan(shell)