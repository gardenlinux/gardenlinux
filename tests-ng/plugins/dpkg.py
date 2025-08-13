import pytest
from .shell import ShellRunner

class Dpkg:
    def __init__(self, shell: ShellRunner):
        self._shell = shell

    def package_is_installed(self, package: str) -> bool:
        result = self._shell(f'dpkg --status {package}', capture_output=True, ignore_exit_code=True)
        return result.returncode == 0
