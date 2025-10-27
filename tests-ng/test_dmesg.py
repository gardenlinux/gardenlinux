import re
from pathlib import Path

import pytest


@pytest.mark.feature("server", reason="needs server feature")
def test_dmesg_sysctl_config():
    config_file = "/etc/sysctl.d/40-allow-nonroot-dmesg.conf"
    assert Path(config_file).exists()
    assert re.search(r"kernel\.dmesg_restrict\s*=\s*0", Path(config_file).read_text())


@pytest.mark.feature("server and booted", reason="sysctl needs a booted system")
def test_dmesg_systctl_runtime(sysctl):
    assert sysctl["kernel.dmesg_restrict"] == 0
