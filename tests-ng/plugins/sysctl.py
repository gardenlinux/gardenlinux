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


class SysctlWrapper:
    def __getitem__(self, key: str):
        path = "/proc/sys/" + key.replace(".", "/")
        with open(path, "r") as f:
            value = f.read().strip()
        return int(value) if value.isdigit() else value

class Sysctl:
    """Collects kernel parameters from /proc/sys/"""

    def __init__(self, shell: ShellRunner):
        self.shell = shell

    def is_sysctl_available(self) -> bool:
        """Check if sysctl is available"""
        try:
            result = self.shell("command -v sysctl", capture_output=True, ignore_exit_code=True)
            return result.returncode == 0
        except Exception:
            return False

    def collect_sysctl_parameters(self) -> dict[str, str]:
        """Collect all readable sysctl parameters, excluding allow-listed ones"""
        if not self.is_sysctl_available():
            return {}

        sysctl_params = {}

        try:
            result = self.shell("sysctl -a 2>/dev/null", capture_output=True, ignore_exit_code=True)
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        sysctl_params[key] = value
        except Exception as e:
            print(f"Warning: Failed to collect sysctl parameters: {e}")

        return dict(sorted(sysctl_params.items()))

@pytest.fixture
def sysctl(request: pytest.FixtureRequest):
    try:
        result = ShellRunner(None)("command -v sysctl", capture_output=True, ignore_exit_code=True)
        if result.returncode != 0:
            pytest.skip("sysctl command not available")
    except Exception:
        pytest.skip("sysctl command not available")
    return SysctlWrapper()

@pytest.fixture
def sysctl_collector(shell: ShellRunner) -> Sysctl:
    return Sysctl(shell)
