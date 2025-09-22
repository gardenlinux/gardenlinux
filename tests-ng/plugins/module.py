import pytest
from .shell import ShellRunner

class Module:
    def __init__(self, shell: ShellRunner):
        self._shell = shell

    def is_module_loaded(self, module: str) -> bool:
        result = self._shell(f"lsmod | grep ^{module}", capture_output=True, ignore_exit_code=True)
        return result.returncode == 0
    def load_module(self, module: str) -> bool:
        result = self._shell(f"modprobe {module}", capture_output=True, ignore_exit_code=False)
        return result.returncode == 0
    def unload_module(self, module: str) -> bool:
        result = self._shell(f"rmmod {module}", capture_output=True, ignore_exit_code=True)
        return result.returncode == 0

@pytest.fixture
def module(shell: ShellRunner) -> Module:
        return Module(shell)
