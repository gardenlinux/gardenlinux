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
                    with open(file_path, "r") as f:
                        value = f.read().strip()
                        sysctl_params[key] = value
                except (PermissionError, FileNotFoundError, IsADirectoryError):
                    # Skip unreadable or transient entries
                    continue
                except Exception:
                    # Be robust: skip any unexpected errors for individual files
                    continue

        return dict(sorted(sysctl_params.items()))

@pytest.fixture
def sysctl(shell: ShellRunner) -> Sysctl:
    return Sysctl(shell)
