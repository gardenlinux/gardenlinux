import re
from pathlib import Path

import pytest


@pytest.mark.feature("server", reason="needs server feature")
def test_sudo_resets_user_environment():
    config_file = "/etc/sudoers"
    assert Path(config_file).exists()
    assert re.search(
        r"(?m)^\s*(?!#)Defaults\s*env_reset", Path(config_file).read_text()
    )
