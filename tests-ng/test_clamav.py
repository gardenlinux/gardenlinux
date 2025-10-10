from pathlib import Path
import pytest
from plugins.dpkg import Dpkg
from plugins.shell import ShellRunner
import shutil


@pytest.mark.feature("clamav")
def test_clamav_is_installed(dpkg: Dpkg):
    assert dpkg.package_is_installed("clamav"), "clamav is not installed"


@pytest.mark.parametrize("binary", ["freshclam", "clamscan"])
@pytest.mark.feature("clamav")
def test_clamav_binaries_are_available(shell: ShellRunner, binary):
    binary_path = shutil.which(binary)
    result = shell(f"{binary_path} --version", capture_output=True)
    assert "ClamAV" in result.stdout, f"Expected being able to call {binary_path}"


@pytest.mark.root(reason="File is only readable by root")
@pytest.mark.feature("clamav")
def test_clamscan_cronjob_is_setup():
    crontab = Path("/var/spool/cron/crontabs/root").read_text()
    assert "/usr/bin/clamscan" in crontab, "Expected cronjob for clamscan"
