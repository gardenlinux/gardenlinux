import pytest
from plugins.parse_file import ParseFile

CONFIG_FILE = "/etc/profile.d/50-nohistory.sh"


@pytest.mark.setting_ids(
    [
        "GL-SET-server-script-profile-nohistory",
    ]
)
@pytest.mark.feature("server")
def test_history_profile_d_contains_required_configuration(parse_file: ParseFile):
    sorted_lines = parse_file.lines(CONFIG_FILE, ordered=True)
    assert [
        "HISTFILE=/dev/null",
        "readonly HISTFILE",
        "export HISTFILE",
    ] in sorted_lines


@pytest.mark.feature("server")
def test_histfile_env_var_is_readonly(shell):
    res = shell(
        ". /etc/profile.d/50-nohistory.sh && HISTFILE=/tmp/owned",
        capture_output=True,
        ignore_exit_code=True,
    )

    assert res.returncode == 2
    assert "HISTFILE: is read only" in res.stderr
