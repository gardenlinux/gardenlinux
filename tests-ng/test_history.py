from pathlib import Path

import pytest
from plugins.parse_file import ParseFile

CONFIG_FILE = "/etc/profile.d/50-nohistory.sh"


@pytest.mark.feature("server")
def test_history_profile_d_contains_required_configuration(parse_file: ParseFile):
    assert parse_file.has_lines(
        CONFIG_FILE,
        [
            "HISTFILE=/dev/null",
            "readonly HISTFILE",
            "export HISTFILE",
        ],
    )


@pytest.mark.feature("server")
def test_histfile_env_var_is_readonly(shell):
    res = shell(
        ". /etc/profile.d/50-nohistory.sh && HISTFILE=/tmp/owned",
        capture_output=True,
        ignore_exit_code=True,
    )

    assert res.returncode == 2
    assert "HISTFILE: is read only" in res.stderr
