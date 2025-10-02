import pytest
from dataclasses import dataclass
from .shell import ShellRunner


@dataclass
class LoadedKernelModule:
    """Represents a loaded kernel module"""
    name: str

    def __str__(self) -> str:
        return self.name


# This Class is used to load, unload or check the Kernel module status
class KernelModule:
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

    def collect_loaded_modules(self) -> list[str]:
        """Collect all currently loaded kernel modules"""
        result = self._shell("lsmod", capture_output=True, ignore_exit_code=True)
        modules = []
        for line in result.stdout.strip().split('\n')[1:]:  # Skip header
            if line.strip():
                module_name = line.split()[0]
                modules.append(module_name)
        return sorted(modules)

@pytest.fixture
def kernel_module(shell: ShellRunner) -> KernelModule:
        return KernelModule(shell)
