import re
from dataclasses import dataclass

import pytest
from plugins.shell import ShellRunner
from plugins.systemd import Systemd


@dataclass
class NtpServer:
    ip: str
    hostname: str


@dataclass
class TimeSyncStatus:
    """output of timedatectl show"""

    ntp: bool
    ntp_synchronized: bool
    poll_interval_max: float


def _parse_duration(s: str) -> float:
    """Parse a duration string like '34min 8s' or '1h 2min 3s' into seconds."""
    total = 0.0
    for match in re.finditer(r"(\d+(?:\.\d+)?)\s*(h|min|s|ms|us)", s):
        value, unit = float(match.group(1)), match.group(2)
        if unit == "h":
            total += value * 3600
        elif unit == "min":
            total += value * 60
        elif unit == "s":
            total += value
        elif unit == "ms":
            total += value / 1000
        elif unit == "us":
            total += value / 1_000_000
    return total


class TimeDateCtl:
    def __init__(self, systemd: Systemd, shell: ShellRunner):
        self._shell = shell
        self._systemd = systemd

    def has_timesync_installed(self) -> bool:
        """Check if systemd-timesyncd.service exists in the image."""
        units = self._systemd.list_installed_units()
        return any(u.unit == "systemd-timesyncd.service" for u in units)

    def is_timesyncd_active(self) -> bool:
        """Check if systemd-timesyncd is active."""
        return self._systemd.is_active("systemd-timesyncd.service")

    def get_ntpserver(self) -> NtpServer:
        """
        Command returns output like this:

            gardenlinux@localhost:~$ timedatectl timesync-status
            Server: 139.162.187.236 (2.debian.pool.ntp.org)
            Poll interval: 2min 8s (min: 32s; max 34min 8s)
            Leap: normal
            Version: 4
            Stratum: 2
            Reference: 3E1E0C34
            Precision: 1us (-23)
            Root distance: 18.370ms (max: 5s)
            Offset: +1.769ms
            Delay: 17.248ms
            Jitter: 668us
            Packet count: 2
            Frequency: +6.910ppm
        """
        result = self._shell(
            cmd="timedatectl timesync-status",
            capture_output=True,
            ignore_exit_code=True,
        )
        if result.returncode != 0:
            raise ValueError(f"timedatectl failed: {result.stderr}")

        line = [
            line.strip()
            for line in result.stdout.split("\n")
            if result.stdout.strip().startswith("Server:")
        ]
        line = line[0] if len(line) > 0 else ""
        pattern = (
            r"Server: (?P<ip>[^ ]+) \((?P<hostname>[^)]+)\)"
            # hostname field can contain an ip
            # example: Server: 169.254.169.123 (169.254.169.123)
        )
        match = re.search(pattern, line)
        if match and match.group("ip") and match.group("hostname"):
            return NtpServer(match.group("ip"), match.group("hostname"))

        raise ValueError(f"no server information available. Got: {result.stdout}")

    def get_timesync_status(self) -> TimeSyncStatus:
        """
        Command returns output like this:

        gardenlinux@localhost:~$ timedatectl show
        Timezone=Etc/UTC
        LocalRTC=no
        CanNTP=yes
        NTP=yes
        NTPSynchronized=yes
        TimeUSec=Tue 2025-09-16 07:01:33 UTC
        RTCTimeUSec=Tue 2025-09-16 07:01:33 UTC
        """
        result = self._shell(
            cmd="timedatectl show", capture_output=True, ignore_exit_code=True
        )
        if result.returncode != 0:
            raise ValueError(f"timedatectl failed: {result.stderr}")

        output = dict(
            [
                line.strip().split("=")
                for line in result.stdout.splitlines()
                if len(line.strip()) > 0
            ]
        )
        return TimeSyncStatus(
            ntp=(output["NTP"] == "yes"),
            ntp_synchronized=(output["NTPSynchronized"] == "yes"),
            poll_interval_max=self._get_poll_interval_max(),
        )

    def _get_poll_interval_max(self) -> float:
        """
        Parse max poll interval from timedatectl timesync-status output like:
            Poll interval: 2min 8s (min: 32s; max 34min 8s)
        Returns the max poll interval in seconds.
        """
        result = self._shell(
            cmd="timedatectl timesync-status",
            capture_output=True,
            ignore_exit_code=True,
        )
        if result.returncode != 0:
            raise ValueError(f"timedatectl timesync-status failed: {result.stderr}")

        for line in result.stdout.splitlines():
            if line.strip().startswith("Poll interval:"):
                match = re.search(r"max\s+([^)]+)\)", line)
                if match:
                    return _parse_duration(match.group(1).strip())

        raise ValueError(f"Could not parse poll interval from: {result.stdout}")


@pytest.fixture
def timedatectl(systemd: Systemd, shell: ShellRunner) -> TimeDateCtl:
    return TimeDateCtl(systemd=systemd, shell=shell)
