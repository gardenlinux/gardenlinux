import subprocess

import pytest

from .shell import ShellRunner


class Ports:
    def __init__(self, shell: ShellRunner):
        self._shell = shell
        try:
            result = shell("ss -tuln", capture_output=True)
        except FileNotFoundError:
            raise RuntimeError("ss not found in PATH")
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                f"ss call failed (exit {exc.returncode})\n"
                f"stderr: {exc.stderr.strip()}"
            )

        open_ports = set()
        for line in result.stdout.splitlines():
            if "LISTEN" in line:
                port = line.split()[4].split(":")[-1]
                if port.isdigit():
                    open_ports.add(int(port))
        self.open_ports = open_ports


@pytest.fixture
def ports(request: pytest.FixtureRequest, shell) -> Ports:
    return Ports(shell)
