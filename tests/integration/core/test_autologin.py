import re

import pytest
from plugins.parse_file import ParseFile

CONFIG_FILES = [
    "/etc/systemd/system/serial-getty@.service.d/autologin.conf",
    "/etc/systemd/system/getty@tty1.service.d/autologin.conf",
]


@pytest.mark.testcov(
    [
        "GL-TESTCOV-_iso-service-getty-tty1-autologin",
        "GL-TESTCOV-_iso-service-serial-getty-autologin",
    ]
)
@pytest.mark.parametrize("config_file", CONFIG_FILES)
@pytest.mark.feature("server and (_dev or _iso)", reason="needs systemd")
def test_autologin(config_file, parse_file: ParseFile):
    lines = parse_file.lines(config_file)
    assert re.compile(r"ExecStart.*autologin") in lines
