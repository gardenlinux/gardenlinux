import functools
import os
import re
from dataclasses import dataclass

import pytest

from .find import FIND_RESULT_TYPE_FILE, Find
from .kernel_versions import KernelVersions
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
    """Manage and inspect kernel modules (loaded/available) for the running kernel."""

    def __init__(self, find: Find, shell: ShellRunner, kernel_versions: KernelVersions):
        self._find = find
        self._shell = shell
        self._kernel_versions = kernel_versions
        self._unload = {}

    def is_module_loaded(self, module: str) -> bool:
        """Return True if ``module`` appears in ``/proc/modules``."""
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
        """Load ``module`` using ``modprobe``; return True on success."""
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
        """Unload ``module`` using ``rmmod``; return True on success."""
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
                    print(
                        f"Unloading {module} exited with status code {result.returncode}"
                    )
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

    def collect_available_modules(self) -> list[str]:
        """Collect all available kernel modules for the currently running kernel."""
        modules: list[str] = []
        try:
            kernel_ver = self._kernel_versions.get_running()
            modules_dir = kernel_ver.modules_dir
            # find modules and compressed modules (e.g. .ko, .ko.xz, .ko.zst)
            pattern = re.compile(r"^(?P<name>.+?)\.ko(?:\..+)?$")
            self._find.same_mnt_only = False
            self._find.root_paths = [modules_dir]
            self._find.entry_type = FIND_RESULT_TYPE_FILE
            for file in self._find:
                basename = os.path.basename(file)
                m = pattern.match(basename)
                if not m:
                    continue
                modules.append(m.group("name"))
        except Exception:
            return []
        return sorted(modules)

    def is_module_available(self, module: str) -> bool:
        """Check if a module is available as loadable module"""
        return module in self.collect_available_modules()

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
def kernel_module(
    find: Find, shell: ShellRunner, kernel_versions: KernelVersions
) -> KernelModule:
    return KernelModule(find, shell, kernel_versions)
