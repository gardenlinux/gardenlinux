import re
from pathlib import Path

import pytest

CONFIG_FILES = {
    "gardener": "/etc/sysctl.d/40-allow-nonroot-dmesg.conf",
    "server and not gardener": "/etc/sysctl.d/40-restric-dmesg.conf",
    "stig": "/etc/sysctl.d/99-stig.conf",
}

# server adds /etc/sysctl.d/40-restric-dmesg.conf, gardener excludes it
# and adds /etc/sysctl.d/40-allow-nonroot-dmesg.conf


@pytest.mark.parametrize(
    "config_file",
    [pytest.param(value, marks=pytest.mark.feature(key)) for key, value in CONFIG_FILES.items()],
    ids=list(CONFIG_FILES.keys()),
)
def test_dmesg_sysctl_config_file_exists(config_file):
    assert Path(config_file).exists()


@pytest.mark.parametrize(
    "config_file",
    [pytest.param(value, marks=pytest.mark.feature(key)) for key, value in CONFIG_FILES.items()],
    ids=list(CONFIG_FILES.keys()),
)
def test_dmesg_sysctl_no_restrictions_on_accessing_dmesg(config_file):
    pattern = re.compile(
        r"""
            ^\s*    # any whitespace in the beginning of the line is allowed
            (?!\#)  # fail the search if a comment character is found
            kernel\.dmesg_restrict\s*=\s*0
        """,
        re.VERBOSE | re.MULTILINE,
    )
    assert re.search(pattern, Path(config_file).read_text())


@pytest.mark.booted(reason="sysctl needs a booted system")
@pytest.mark.feature("server or gardener or stig")
def test_dmesg_systctl_runtime(sysctl):
    assert sysctl["kernel.dmesg_restrict"] == "0"


@pytest.mark.booted(reason="needs a booted system with dmesg restrictions loaded")
@pytest.mark.feature("server or gardener or stig")
def test_dmesg_call_by_unprivileged_user_works(shell):
    assert shell("id -u", capture_output=True).stdout.strip() != "0"
    res = shell("dmesg", capture_output=False, ignore_exit_code=True)
    assert res.returncode == 0
