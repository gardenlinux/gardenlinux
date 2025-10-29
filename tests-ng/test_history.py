import re
from pathlib import Path

import pytest


@pytest.mark.feature("server", reason="needs server feature")
def test_history_profile_d():
    config_file = "/etc/profile.d/50-nohistory.sh"
    config_contents = Path(config_file).read_text()

    assert Path(config_file).exists()

    assert re.search(r"HISTFILE=/dev/null", config_contents)
    assert re.search(r"readonly HISTFILE", config_contents)
    assert re.search(r"export HISTFILE", config_contents)


@pytest.mark.feature("server", reason="needs server feature")
def test_histfile_env_var_is_readonly(shell):
    res = shell("HISTFILE=/tmp/owned", capture_output=False, ignore_exit_code=False)

    assert res.returncode == 1
    assert "HISTFILE: readonly variable" in res.stderr
