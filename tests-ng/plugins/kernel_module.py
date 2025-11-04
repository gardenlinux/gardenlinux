import functools
import re
from dataclasses import dataclass

import pytest

from .shell import ShellRunner

dependencies = re.compile("/([^/]*)\\.ko")


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
        self._unload = {}

    def is_module_loaded(self, module: str) -> bool:
        try:
            with open("/proc/modules", "r") as f:
                for line in f:
                    if not line:
                        continue
                    # /proc/modules format: name size usecount deps state address
                    name = line.split()[0]
                    if name == module:
                        return True
        except Exception:
            pass
        return False

    def load_module(self, module: str) -> bool:
        result = self._shell(
            f"modprobe {module}", capture_output=True, ignore_exit_code=False
        )
        return result.returncode == 0

    def safe_load_module(self, module: str) -> bool:
        self._unload = (
            self.module_dependencies(module, check_loaded=True) | self._unload
        )
        result = self._shell(
            f"modprobe {module}", capture_output=True, ignore_exit_code=False
        )
        print(self._unload)
        return result.returncode == 0

    def unload_module(self, module: str) -> bool:
        result = self._shell(
            f"rmmod {module}", capture_output=True, ignore_exit_code=True
        )
        return result.returncode == 0

    def safe_unload_modules(self) -> bool:
        success = True
        print(self._unload)
        while len(self._unload) > 0:
            for module in self._unload:
                independent = True
                for dependency in self._unload:
                    if module != dependency and module in self._unload[dependency]:
                        independent = False
                        break

                if independent:
                    del self._unload[module]
                    result = self._shell(
                        f"rmmod {module}", capture_output=True, ignore_exit_code=True
                    )
                    print(f"Unloading {module} exited with status code {result.returncode}")
                    print(f"stdout: {result.stdout}")
                    print(f"stderr: {result.stderr}")
                    success = success and result.returncode == 0
                    break
            print(self._unload)
        return success

    def collect_loaded_modules(self) -> list[str]:
        """Collect all currently loaded kernel modules"""
        modules: list[str] = []
        try:
            with open("/proc/modules", "r") as f:
                for line in f:
                    if not line.strip():
                        continue
                    modules.append(line.split()[0])
        except Exception:
            return []
        return sorted(modules)

    def module_dependencies(
        self, module: str, check_loaded: bool = False
    ) -> dict[str, set[str]]:
        result = self._shell(f"modprobe --show-depends {module}", capture_output=True)

        deps = {module: set()}
        for dependency in dependencies.findall(result.stdout):
            if module != dependency:
                if not check_loaded or not self.is_module_loaded(dependency):
                    deps[module].add(dependency)
                    deps |= self.module_dependencies(
                        dependency, check_loaded=check_loaded
                    )

        return deps


@pytest.fixture
def kernel_module(shell: ShellRunner) -> KernelModule:
    return KernelModule(shell)
