import os
from dataclasses import dataclass

import pytest

from .kernel_versions import KernelVersions


@dataclass
class KernelConfig:
    """Represents a kernel config"""

    path: str
    version: str
    content: str


class KernelConfigs:
    """Access kernel config files for installed and running kernels under ``/boot``."""

    def __init__(self, kernel_versions: KernelVersions):
        self._kernel_versions = kernel_versions
        self._config_dir = "/boot"

    def get_installed(self) -> list[KernelConfig]:
        """Return ``KernelConfig`` objects for all installed kernels."""
        configs: list[KernelConfig] = []
        for kernel_version in self._kernel_versions.get_installed():
            configs.append(
                KernelConfig(
                    path=os.path.join(
                        self._config_dir, f"config-{kernel_version.version}"
                    ),
                    version=kernel_version.version,
                    content=open(
                        os.path.join(
                            self._config_dir, f"config-{kernel_version.version}"
                        )
                    ).read(),
                )
            )
        return configs

    def get_running(self) -> KernelConfig:
        """Return the ``KernelConfig`` for the currently running kernel."""
        running_kernel = self._kernel_versions.get_running()
        config_path = os.path.join(self._config_dir, f"config-{running_kernel.version}")
        config = KernelConfig(
            path=config_path,
            version=running_kernel.version,
            content=open(config_path).read(),
        )
        return config


@pytest.fixture
def kernel_configs(kernel_versions: KernelVersions) -> KernelConfigs:
    """Fixture providing access to installed and running kernel configs."""
    return KernelConfigs(kernel_versions)
