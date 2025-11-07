from pathlib import Path

import pytest

CONFIG_FILE = "/etc/profile.d/50-nohistory.sh"


@pytest.mark.feature("server")
def test_history_profile_d_file_exists():
    assert Path(CONFIG_FILE).exists()


@pytest.mark.feature("server")
def test_history_profile_d_contains_required_configuration(file_content):
    assert file_content.check_lines(
        CONFIG_FILE, ["HISTFILE=/dev/null", "readonly HISTFILE", "export HISTFILE"]
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
