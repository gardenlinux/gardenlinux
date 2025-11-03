import re
from pathlib import Path

import pytest

CONFIG_FILE = "/etc/sysctl.d/40-allow-nonroot-dmesg.conf"


@pytest.mark.feature("server")
def test_dmesg_sysctl_config_file_exists():
    assert Path(CONFIG_FILE).exists()


@pytest.mark.feature("server")
def test_dmesg_sysctl_no_restrictions_on_accessing_dmesg():
    pattern = re.compile(
        r"""
            ^\s*    # any whitespace in the beginning of the line is allowed
            (?!\#)  # fail the search if a comment character is found
            kernel\.dmesg_restrict\s*=\s*0
        """,
        re.VERBOSE | re.MULTILINE,
    )
    assert re.search(pattern, Path(CONFIG_FILE).read_text())


@pytest.mark.booted(reason="sysctl needs a booted system")
@pytest.mark.feature("server or stig")
def test_dmesg_systctl_runtime(sysctl):
    assert sysctl["kernel.dmesg_restrict"] == "0"


@pytest.mark.feature("server")
def test_dmesg_call_by_unprivileged_user_works(shell):
    assert shell("id -u", capture_output=True).stdout.strip() != "0"
    res = shell("dmesg", capture_output=False, ignore_exit_code=True)
    assert res.returncode == 0
