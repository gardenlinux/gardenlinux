import os
import re
from dataclasses import dataclass

import pytest

from .find import FIND_RESULT_TYPE_FILE, Find
from .kernel_versions import KernelVersions
from .shell import ShellRunner


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

    def unload_module(self, module: str) -> bool:
        """Unload ``module`` using ``rmmod``; return True on success."""
        result = self._shell(
            f"rmmod {module}", capture_output=True, ignore_exit_code=True
        )
        return result.returncode == 0

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


@pytest.fixture
def kernel_module(
    find: Find, shell: ShellRunner, kernel_versions: KernelVersions
) -> KernelModule:
    return KernelModule(find, shell, kernel_versions)
