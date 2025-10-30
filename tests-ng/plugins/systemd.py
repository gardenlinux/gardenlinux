import json
import re
import time
from dataclasses import dataclass
from typing import Tuple

import pytest

from .modify import allow_system_modifications
from .shell import ShellRunner


@dataclass
class SystemdUnit:
    unit: str
    load: str
    active: str
    sub: str


@dataclass
class SystemRunningState:
    state: str
    returncode: int
    elapsed_time: float


def _seconds(token: str) -> float:
    if token.endswith("ms"):
        return float(token[:-2]) / 1000
    if token.endswith("s"):
        return float(token[:-1])
    raise ValueError(f"Unknown time unit in '{token}'")


def _parse_units(systemctl_stdout: str) -> list[SystemdUnit]:
    units = []
    try:
        unit_entries = json.loads(systemctl_stdout)
        for entry in unit_entries:
            units.append(
                SystemdUnit(
                    unit=entry.get("unit", ""),
                    load=entry.get("load", ""),
                    active=entry.get("active", ""),
                    sub=entry.get("sub", ""),
                )
            )
    except json.JSONDecodeError:
        pass
    return units


class Systemd:
    def __init__(self, shell: ShellRunner):
        self._shell = shell
        self._systemctl = "systemctl --plain --no-legend --no-pager --output=json"

    def analyze(self) -> Tuple[float, ...]:
        result = self._shell(
            "systemd-analyze", capture_output=True, ignore_exit_code=True
        )
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

    def is_active(self, unit_name: str) -> bool:
        result = self._shell(
            f"{self._systemctl} is-active {unit_name}",
            capture_output=True,
            ignore_exit_code=True,
        )
        active = result.stdout.strip() == "active"
        if not active:
            result_status = self._shell(
                f"{self._systemctl} status {unit_name}",
                capture_output=True,
                ignore_exit_code=True,
            )
            print(result_status.stdout)

        return active

    def start_unit(self, unit_name: str):
        if not allow_system_modifications():
            pytest.skip(
                "starting units is only supported when system state modifications are allowed"
            )
        self._shell(f"{self._systemctl} start {unit_name}")

    def stop_unit(self, unit_name: str):
        if not allow_system_modifications():
            pytest.skip(
                "stopping units is only supported when system state modifications are allowed"
            )
        self._shell(f"{self._systemctl} stop {unit_name}")

    def list_units(self) -> list[SystemdUnit]:
        result = self._shell(
            f"{self._systemctl}", capture_output=True, ignore_exit_code=True
        )
        return _parse_units(result.stdout)

    def list_failed_units(self) -> list[SystemdUnit]:
        result = self._shell(
            f"{self._systemctl} --failed", capture_output=True, ignore_exit_code=True
        )
        return _parse_units(result.stdout)

    def wait_is_system_running(self) -> SystemRunningState:
        start_time = time.time()
        result = self._shell(
            f"{self._systemctl} is-system-running --wait",
            capture_output=True,
            ignore_exit_code=True,
        )
        elapsed = time.time() - start_time
        return SystemRunningState(result.stdout.strip(), result.returncode, elapsed)


@pytest.fixture
def systemd(shell: ShellRunner):
    return Systemd(shell)
