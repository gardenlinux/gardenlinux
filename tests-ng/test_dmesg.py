import re
from pathlib import Path

import pytest

CONFIG = {
    "gardener": {
        "file_path": "/etc/sysctl.d/40-allow-nonroot-dmesg.conf",
        "is_user_restricted": False,
    },
    "server and not gardener": {
        "file_path": "/etc/sysctl.d/40-restric-dmesg.conf",
        "is_user_restricted": True,
    },
    "stig": {"file_path": "/etc/sysctl.d/99-stig.conf", "is_user_restricted": True},
}

# server adds /etc/sysctl.d/40-restric-dmesg.conf, gardener excludes it
#    and adds /etc/sysctl.d/40-allow-nonroot-dmesg.conf instead


@pytest.mark.parametrize(
    "config_file",
    [
        pytest.param(value["file_path"], marks=pytest.mark.feature(key))
        for key, value in CONFIG.items()
    ],
    ids=list(CONFIG.keys()),
)
def test_dmesg_sysctl_config_file_exists(config_file):
    assert Path(config_file).exists()


@pytest.mark.parametrize(
    ("config_file", "is_user_restricted"),
    [
        pytest.param(
            value["file_path"],
            value["is_user_restricted"],
            marks=pytest.mark.feature(key),
        )
        for key, value in CONFIG.items()
    ],
    ids=list(CONFIG.keys()),
)
def test_dmesg_sysctl_restrictions_on_accessing_dmesg(config_file, is_user_restricted):
    sysctl_toggle = 1 if is_user_restricted else 0
    pattern = re.compile(
        rf"""
            ^\s*    # any whitespace in the beginning of the line is allowed
            (?!\#)  # fail the search if a comment character is found
            kernel\.dmesg_restrict\s*=\s*{sysctl_toggle}
        """,
        re.VERBOSE | re.MULTILINE,
    )
    assert re.search(pattern, Path(config_file).read_text())


@pytest.mark.parametrize(
    ("config_file", "is_user_restricted"),
    [
        pytest.param(
            value["file_path"],
            value["is_user_restricted"],
            marks=pytest.mark.feature(key),
        )
        for key, value in CONFIG.items()
    ],
    ids=list(CONFIG.keys()),
)
@pytest.mark.booted(reason="sysctl needs a booted system")
def test_dmesg_sysctl_runtime(config_file, is_user_restricted, sysctl):
    sysctl_toggle = "1" if is_user_restricted else "0"
    assert sysctl["kernel.dmesg_restrict"] == sysctl_toggle


@pytest.mark.booted(reason="needs a booted system with dmesg restrictions loaded")
@pytest.mark.feature("gardener")
def test_dmesg_call_by_unprivileged_user_works(shell):
    res = shell("dmesg", capture_output=False, ignore_exit_code=True)
    assert res.returncode == 0
