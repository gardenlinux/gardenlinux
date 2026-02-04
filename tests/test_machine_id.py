import re
from pathlib import Path

import pytest
from plugins.parse_file import ParseFile


@pytest.mark.testcov(["GL-TESTCOV-server-config-machine-id"])
@pytest.mark.booted(reason="sysctl needs a booted system")
def test_machine_id_is_initialized(parse_file: ParseFile):
    lines = parse_file.lines("/etc/machine-id")
    assert re.compile(r"^[0-9a-f]{32}$") in lines
