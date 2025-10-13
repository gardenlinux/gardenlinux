import os
import pytest
from dataclasses import dataclass
from .shell import ShellRunner


@dataclass
class SysctlParam:
    """Represents a sysctl parameter"""
    name: str
    value: str

    def __str__(self) -> str:
        return f"{self.name}={self.value}"


class Sysctl:
    """Collects kernel parameters from /proc/sys/"""

    def __init__(self, shell: ShellRunner):
        self.shell = shell

    def _read_sysctl_parameter(self, key: str) -> str:
        """Read a single sysctl parameter from /proc/sys"""
        # Convert sysctl key to file path: replace '.' with '/'
        file_path = f"/proc/sys/{key.replace('.', '/')}"

        try:
            with open(file_path, "r") as f:
                return f.read().strip()
        except (PermissionError, FileNotFoundError, IsADirectoryError):
            # Skip unreadable or transient entries
            raise KeyError(f"Sysctl parameter '{key}' not found")
        except Exception:
            # Be robust: skip any unexpected errors
            raise KeyError(f"Sysctl parameter '{key}' not found")

    def collect_sysctl_parameters(self) -> dict[str, str]:
        """Collect all readable sysctl parameters by parsing /proc/sys recursively."""
        sysctl_params: dict[str, str] = {}

        base_path = "/proc/sys"
        if not os.path.isdir(base_path):
            return {}

        for root, _dirs, files in os.walk(base_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                # Build sysctl key: strip base_path and replace '/' with '.'
                rel_path = file_path[len(base_path) + 1:]
                key = rel_path.replace("/", ".")
                try:
                    value = self._read_sysctl_parameter(key)
                    sysctl_params[key] = value
                except KeyError:
                    # Skip unreadable or transient entries
                    continue

        return dict(sorted(sysctl_params.items()))

    def __getitem__(self, key: str) -> str:
        """Enable dictionary-style access to sysctl parameters"""
        return self._read_sysctl_parameter(key)

@pytest.fixture
def sysctl(shell: ShellRunner) -> Sysctl:
    return Sysctl(shell)
