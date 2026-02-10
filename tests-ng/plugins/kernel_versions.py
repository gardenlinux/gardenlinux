import os
from dataclasses import dataclass

import pytest


@dataclass
class KernelVersion:
    """Represents a kernel version"""

    version: str
    modules_dir: str

    def __str__(self) -> str:
        return self.version

    def __lt__(self, other: "KernelVersion") -> bool:
        """Compare kernel versions for sorting."""
        return self.version < other.version


class KernelVersions:
    """Inspect installed and running kernel versions via ``/lib/modules`` and ``uname``."""

    def __init__(self):
        self._modules_dir = "/lib/modules"

    def get_installed(self) -> list[KernelVersion]:
        """Get all installed kernel versions."""
        kernel_versions: list[KernelVersion] = []
        if not os.path.exists(self._modules_dir):
            return []

        for item in os.listdir(self._modules_dir):
            item_path = os.path.join(self._modules_dir, item)
            if os.path.isdir(item_path):
                kernel_versions.append(
                    KernelVersion(version=item, modules_dir=item_path)
                )

        return sorted(kernel_versions)

    def get_running(self) -> KernelVersion:
        """Get the running kernel version."""
        version_str = os.uname().release
        return KernelVersion(
            version=version_str,
            modules_dir=os.path.join(self._modules_dir, version_str),
        )


@pytest.fixture
def kernel_versions() -> KernelVersions:
    """Fixture providing access to installed and running kernel versions."""
    return KernelVersions()
