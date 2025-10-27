import re
from pathlib import Path

import pytest

CONFIG_FILES = [
    "/etc/systemd/system/serial-getty@.service.d/autologin.conf",
    "/etc/systemd/system/getty@tty1.service.d/autologin.conf",
]


@pytest.mark.parametrize("config_file", CONFIG_FILES)
@pytest.mark.feature("server and (_dev or _iso)", reason="needs systemd")
def test_autologin(config_file):
    assert Path(config_file).exists()
    assert re.search("ExecStart.*autologin", Path(config_file).read_text())
