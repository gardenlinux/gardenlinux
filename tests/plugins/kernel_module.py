import logging
import os
import re
import time
from dataclasses import dataclass
from graphlib import TopologicalSorter

import pytest

from .find import FIND_RESULT_TYPE_FILE, Find
from .kernel_versions import KernelVersions
from .shell import ShellRunner

dependencies = re.compile("/([^/]*)\\.ko")

logger = logging.getLogger(__name__)


@dataclass
class LoadedKernelModule:
    """Represents a loaded kernel module"""

    name: str

    def __str__(self) -> str:
        return self.name


class KernelModule:
    """Manage and inspect kernel modules (loaded/available) for the running kernel."""

    def __init__(self, find: Find, shell: ShellRunner, kernel_versions: KernelVersions):
        self._find = find
        self._shell = shell
        self._kernel_versions = kernel_versions
        self._initially_loaded = set(self.collect_loaded_modules())
        self._loaded: set[str] = set()
        self._dependency_graph: dict[str, set[str]] = {}

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

    def get_module_parameter(self, module: str, parameter: str) -> str | None:
        """Get the value of a module parameter.

        Returns the parameter value as a string, or None if the parameter doesn't exist
        or the module is not loaded.

        Args:
            module: The name of the kernel module
            parameter: The name of the parameter to retrieve

        Returns:
            The parameter value as a string, or None if not found
        """
        param_path = f"/sys/module/{module}/parameters/{parameter}"
        try:
            with open(param_path, "r") as f:
                return f.read().strip()
        except Exception:
            return None

    def has_module_parameter(
        self, module: str, parameter: str, expected_value: str
    ) -> bool:
        """Check if a module parameter has a specific value.

        Args:
            module: The name of the kernel module
            parameter: The name of the parameter to check
            expected_value: The expected value of the parameter

        Returns:
            True if the parameter exists and matches the expected value, False otherwise
        """
        actual_value = self.get_module_parameter(module, parameter)
        return actual_value == expected_value

    def get_module_parameters(self, module: str) -> dict[str, str]:
        """Get all parameters for a loaded module.

        Args:
            module: The name of the kernel module

        Returns:
            A dictionary mapping parameter names to their values.
            Returns an empty dict if the module is not loaded or has no parameters.
        """
        params = {}
        params_dir = f"/sys/module/{module}/parameters"
        try:
            if os.path.exists(params_dir):
                for param_name in os.listdir(params_dir):
                    param_path = os.path.join(params_dir, param_name)
                    if os.path.isfile(param_path):
                        try:
                            with open(param_path, "r") as f:
                                params[param_name] = f.read().strip()
                        except Exception:
                            # Some parameters may not be readable
                            pass
        except Exception:
            pass
        return params

    def load_module(self, module: str) -> bool:
        """Load ``module`` using ``modprobe`` and track all modules that were loaded.
        Only tracks modules that were not initially loaded.
        Returns True on success or if the module is already loaded.
        """
        before_loaded = set(self.collect_loaded_modules())

        if self.is_module_loaded(module):
            if module not in self._initially_loaded and module not in self._loaded:
                self._loaded.add(module)
                if module not in self._dependency_graph:
                    self._dependency_graph[module] = set()
                self._update_module_dependencies(module)
            return True

        result = self._shell(
            f"modprobe {module}", capture_output=True, ignore_exit_code=False
        )

        if result.returncode != 0:
            return False

        after_loaded = set(self.collect_loaded_modules())
        newly_loaded = after_loaded - before_loaded

        modules_to_track = []
        for new_module in newly_loaded:
            if new_module not in self._initially_loaded:
                self._loaded.add(new_module)
                modules_to_track.append(new_module)
                if new_module not in self._dependency_graph:
                    self._dependency_graph[new_module] = set()

        for mod in modules_to_track:
            self._update_module_dependencies(mod)

        return True

    def _update_module_dependencies(self, module: str) -> None:
        """Update the dependency graph for a module."""
        dep_result = self._shell(
            f"modprobe --show-depends {module}", capture_output=True
        )
        for dependency in dependencies.findall(dep_result.stdout):
            if dependency != module:
                # Only track dependencies that we also loaded (not initially loaded)
                if dependency in self._loaded:
                    self._dependency_graph[module].add(dependency)

    def unload_module(self, module: str) -> bool:
        """Unload ``module`` using ``rmmod``; return True on success.
        Uses ``rmmod`` instead of ``modprobe -r`` to avoid automatically unloading
        dependencies that were initially loaded."""
        logger.debug(f"KernelModule.unload_module: about to call 'rmmod {module}'")
        result = self._shell(
            f"rmmod {module}",
            capture_output=True,
            ignore_exit_code=True,
        )
        logger.debug(f"rmmod stdout: <<{result.stdout}>>")
        if result.returncode != 0:
            logger.warning(
                f"rmmod {module} failed with return code {result.returncode}: {result.stderr}"
            )
        else:
            logger.debug(f"rmmod stderr: <<{result.stderr}>>")
        return result.returncode == 0

    def _verify_module_unloaded(
        self, module: str, max_wait: int = 60
    ) -> tuple[bool, int]:
        """Verify that a module is actually unloaded, checking every second.
        Returns (success, waited_seconds) where success is True if module is unloaded.
        """
        waited = 0
        while self.is_module_loaded(module) and waited < max_wait:
            time.sleep(1)
            waited += 1

        if self.is_module_loaded(module):
            return False, waited
        return True, waited

    def _unload_and_verify(self, module: str) -> bool:
        """Unload a module and verify it's actually unloaded.
        Returns True if successfully unloaded, False otherwise."""
        unload_result = self.unload_module(module)

        if not unload_result:
            if self.is_module_loaded(module):
                logger.warning(
                    f"rmmod failed for {module} but module is still loaded. "
                    f"This might indicate the module is still in use or there's a dependency issue."
                )
            return False

        success, waited = self._verify_module_unloaded(module)
        if success:
            logger.debug(
                f"Module {module} successfully unloaded after {waited} seconds"
            )
        else:
            logger.warning(
                f"Module {module} is still loaded after {waited} seconds "
                f"despite rmmod returning success. This might indicate the module "
                f"is still in use by another module or process."
            )
        return success

    def _calculate_unload_order(self) -> list[str]:
        """Calculate the order to unload modules (dependents before dependencies).

        For kernel modules: if module A depends on B (A uses B), we must unload A before B.
        This is because B cannot be unloaded while A is still using it.

        Uses TopologicalSorter: we add edges as add(module, dependency), which means
        "module depends on dependency". static_order() returns dependencies before dependents
        (load order), so we reverse it to get dependents before dependencies (unload order).
        """
        sorter = TopologicalSorter()

        for module in self._loaded:
            sorter.add(module)

        for module, deps in self._dependency_graph.items():
            for dep in deps:
                if dep in self._loaded:
                    sorter.add(module, dep)

        try:
            order = list(sorter.static_order())
            return list(reversed(order))
        except ValueError as e:
            # Cycle detected
            logger.warning(
                f"Cycle detected in dependency graph: {e}. "
                f"Unloading modules in arbitrary order."
            )
            return list(self._loaded)

    def unload_modules(self) -> bool:
        """Unload all modules loaded by ``load_module`` in the correct order using ``rmmod``.
        Only unloads modules that we loaded (not initially loaded).
        Returns True if all succeed.
        """
        if not self._loaded:
            return True

        unload_order = self._calculate_unload_order()
        success = True

        for module in unload_order:
            if module in self._initially_loaded:
                logger.warning(
                    f"Skipping unload of {module} - it was already loaded before this test. "
                    f"This should not happen if tracking is correct."
                )
                continue

            if module not in self._loaded:
                logger.warning(
                    f"Skipping unload of {module} - not in _loaded. "
                    f"This should not happen if tracking is correct."
                )
                continue

            unload_success = self._unload_and_verify(module)
            if not unload_success and self.is_module_loaded(module):
                logger.error(
                    f"Module {module} failed to unload and is still loaded. "
                    f"This will cause sysdiff to detect system changes."
                )
            success &= unload_success

        # Final verification: check if any tracked modules are still loaded
        # This catches cases where modules get reloaded after we unload them
        still_loaded = []
        for module in list(
            self._loaded
        ):  # Use list() to avoid modification during iteration
            if self.is_module_loaded(module) and module not in self._initially_loaded:
                still_loaded.append(module)

        if still_loaded:
            logger.warning(
                f"The following modules are still loaded after unload attempt: {still_loaded}. "
                f"Trying to unload them again."
            )
            # Try unloading again - they might have been reloaded by udev or another process
            for module in still_loaded:
                logger.debug(f"Retrying unload of {module}")
                retry_success = self._unload_and_verify(module)
                if not retry_success:
                    logger.error(
                        f"Module {module} failed to unload on retry. "
                        f"This will cause sysdiff to detect system changes."
                    )
                success &= retry_success

        self._loaded.clear()
        self._dependency_graph.clear()
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
