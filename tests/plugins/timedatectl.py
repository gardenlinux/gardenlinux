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
    poll_interval_max: int


UNITS = {
    "s": 1,
    "sec": 1,
    "second": 1,
    "seconds": 1,
    "m": 60,
    "min": 60,
    "minute": 60,
    "minutes": 60,
    "h": 3600,
    "hr": 3600,
    "hour": 3600,
    "hours": 3600,
    "d": 86400,
    "day": 86400,
    "days": 86400,
    "w": 604800,
    "week": 604800,
    "weeks": 604800,
}


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
            cmd="timedatectl show; timedatectl show-timesync",
            capture_output=True,
            ignore_exit_code=True,
        )
        if result.returncode != 0:
            raise ValueError(f"timedatectl failed: {result.stderr}")

        output = dict(
            [
                line.strip().split("=", maxsplit=1)
                for line in result.stdout.splitlines()
                if len(line.strip()) > 0
            ]
        )
        return TimeSyncStatus(
            ntp=(output["NTP"] == "yes"),
            ntp_synchronized=(output["NTPSynchronized"] == "yes"),
            poll_interval_max=self._human_time_to_seconds(
                output["PollIntervalMaxUSec"]
            ),
        )

    def _human_time_to_seconds(self, time_span: str) -> int:
        """
        Converts human-readable time description
        like "34min 8s" into integer seconds value like 2048.
        Human-readable time spec: https://www.freedesktop.org/software/systemd/man/latest/systemd.time.html#Parsing%20Time%20Spans
        """
        matches = re.findall(r"(\d+)([a-z]+)", time_span.lower())

        if not matches and time_span.strip():
            raise ValueError(f"Invalid time format: '{time_span}'")

        return sum([int(value) * UNITS[unit] for (value, unit) in matches])


@pytest.fixture
def timedatectl(systemd: Systemd, shell: ShellRunner) -> TimeDateCtl:
    return TimeDateCtl(systemd=systemd, shell=shell)
