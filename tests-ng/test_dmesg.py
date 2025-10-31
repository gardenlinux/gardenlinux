import re
from pathlib import Path

import pytest

CONFIG_FILE = "/etc/sysctl.d/40-allow-nonroot-dmesg.conf"


@pytest.mark.feature("server and not metal")
def test_dmesg_sysctl_config_file_exists():
    assert Path(CONFIG_FILE).exists()


@pytest.mark.feature("server and not metal")
def test_dmesg_sysctl_no_restrictions_on_accessing_dmesg():
    pattern = re.compile(
        r"""
            (?m)   # go multiline mode
            ^\s*   # any whitespace in the beginning of the line is allowed
            (?!#)  # fail the search if a comment character is found
            kernel\.dmesg_restrict\s*=\s*0
        """,
        re.VERBOSE,
    )
    assert re.search(pattern, Path(CONFIG_FILE).read_text())


@pytest.mark.booted(reason="sysctl needs a booted system")
@pytest.mark.feature("server and not metal")
def test_dmesg_systctl_runtime(sysctl):
    assert sysctl["kernel.dmesg_restrict"] == 0
