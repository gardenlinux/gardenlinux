import pytest
import re
import shlex
from dataclasses import dataclass

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

class TimeDateCtl:
        def __init__(self, systemd: Systemd, shell: ShellRunner):
            self._shell = shell
            self._systemd = systemd

            assert self._systemd.is_active("systemd-timesyncd.service"), f"systemd-timesyncd must be active"

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
            result = self._shell(cmd="timedatectl timesync-status", capture_output=True, ignore_exit_code=True)
            if result.returncode != 0:
                raise ValueError(f"timedatectl failed: {result.stderr}")

            line = [line.strip() for line in result.stdout.split("\n") if result.stdout.strip().startswith("Server:")]
            line = line[0] if len(line) > 0 else ""
            pattern = r'(\d{1,3}(?:\.\d{1,3}){3}) \(([^)]+)\)'
            match = re.search(pattern, line)
            if match:
                ip = match.group(1)
                hostname = match.group(2)
                return NtpServer(ip=match.group(1), hostname=match.group(2))

            raise ValueError(f"no server information available")

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
            result = self._shell(cmd="timedatectl show", capture_output=True, ignore_exit_code=True)
            if result.returncode != 0:
                raise ValueError(f"timedatectl failed: {result.stderr}")

            output = dict([line.strip().split("=") for line in result.stdout.splitlines() if len(line.strip()) > 0])
            return TimeSyncStatus(ntp=(output["NTP"] == "yes"), ntp_synchronized=(output["NTPSynchronized"] == "yes"))

@pytest.fixture
def timedatectl(systemd: Systemd, shell: ShellRunner):
     return TimeDateCtl(systemd=systemd, shell=shell)
