import re
import pytest
from typing import Tuple, Callable, Any
from .shell import ShellRunner

def _seconds(token: str) -> float:
    if token.endswith("ms"):
        return float(token[:-2]) / 1000
    if token.endswith("s"):
        return float(token[:-1])
    raise ValueError(f"Unknown time unit in '{token}'")

class Systemd:
    def __init__(self, shell: ShellRunner):
        self._shell = shell

    # TODO: we should probably add functionality to check for failed units etc. in here as well

    def analyze(self) -> Tuple[float, ...]:
        result = self._shell("systemd-analyze", capture_output=True, ignore_exit_code=True)
        if result.returncode != 0:
            raise ValueError(f"systemd-analyze failed: {result.stderr}")
        output = result.stdout
        summary = output.splitlines()[0]

        m = re.search(
            r"([\d.]+[a-z]+)\s+\(kernel\).*?"
            r"([\d.]+[a-z]+)\s+\(initrd\).*?"
            r"([\d.]+[a-z]+)\s+\(userspace\)",
            summary,
        )
        if not m:
            raise ValueError(f"Unexpected systemd-analyze output: {summary}")

        return tuple(_seconds(v) for v in m.groups())

    def is_running(self, unit_name: str) -> bool:
        result = self._shell(f"systemctl is-active {unit_name}", capture_output=True, ignore_exit_code=True)
        return result.stdout.strip() == "active"

    def start_unit(self, unit_name: str):
        self._shell(f"systemctl start {unit_name}")


@pytest.fixture
def systemd(shell: ShellRunner):
    return Systemd(shell)
