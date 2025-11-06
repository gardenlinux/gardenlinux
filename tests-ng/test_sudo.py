import re
from pathlib import Path

import pytest


@pytest.mark.feature("server", reason="needs server feature")
def test_sudo_resets_user_environment():
    config_file = "/etc/sudoers"
    pattern = re.compile(
        r"""
        ^\s*    # any whitespace in the beginning of the line is allowed
        (?!\#)  # fail the search if a comment character is found
        Defaults\s*env_reset
        """,
        re.VERBOSE | re.MULTILINE,
    )
    assert Path(config_file).exists()
    assert re.search(pattern, Path(config_file).read_text())
