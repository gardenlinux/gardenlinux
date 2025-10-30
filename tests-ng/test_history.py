import re
from pathlib import Path

import pytest


@pytest.mark.feature("server", reason="needs server feature")
def test_history_profile_d():
    config_file = "/etc/profile.d/50-nohistory.sh"
    config_contents = Path(config_file).read_text()

    assert Path(config_file).exists()

    assert re.search(r"(?m)^\s*(?!#)HISTFILE=/dev/null", config_contents)
    assert re.search(r"(?m)^\s*(?!#)readonly HISTFILE", config_contents)
    assert re.search(r"(?m)^\s*(?!#)export HISTFILE", config_contents)


@pytest.mark.feature("server", reason="needs server feature")
def test_histfile_env_var_is_readonly(shell):
    res = shell(
        ". /etc/profile.d/50-nohistory.sh && HISTFILE=/tmp/owned",
        capture_output=True,
        ignore_exit_code=True,
    )

    assert res.returncode == 2
    assert "HISTFILE: is read only" in res.stderr
