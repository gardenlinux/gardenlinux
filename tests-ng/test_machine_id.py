from pathlib import Path

import pytest
from plugins.parse_file import ParseFile


@pytest.mark.booted(reason="sysctl needs a booted system")
def test_machine_id_is_initialized(parse_file: ParseFile):
    assert parse_file.match_regex("/etc/machine-id", r"^[0-9a-f]{32}$")
