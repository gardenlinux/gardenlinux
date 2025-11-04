import re
from pathlib import Path

import pytest

CONFIG_FILE = "/etc/profile.d/50-nohistory.sh"


@pytest.mark.feature("server", reason="needs server feature")
def test_history_profile_d_file_exists():
    assert Path(CONFIG_FILE).exists()


def test_history_profile_d_contains_required_configuration():
    config_contents = Path(CONFIG_FILE).read_text()

    patterns = [
        re.compile(
            r"""
            ^\s*    # any whitespace in the beginning of the line is allowed
            (?!\#)  # fail the search if a comment character is found
            HISTFILE=/dev/null
        """,
            re.VERBOSE | re.MULTILINE,
        ),
        re.compile(
            r"""
            ^\s*    # any whitespace in the beginning of the line is allowed
            (?!\#)  # fail the search if a comment character is found
            readonly\s*HISTFILE
        """,
            re.VERBOSE | re.MULTILINE,
        ),
        re.compile(
            r"""
            ^\s*    # any whitespace in the beginning of the line is allowed
            (?!\#)  # fail the search if a comment character is found
            export\s*HISTFILE
        """,
            re.VERBOSE | re.MULTILINE,
        ),
    ]

    for pattern in patterns:
        assert re.search(pattern, config_contents)


@pytest.mark.feature("server", reason="needs server feature")
def test_histfile_env_var_is_readonly(shell):
    res = shell(
        ". /etc/profile.d/50-nohistory.sh && HISTFILE=/tmp/owned",
        capture_output=True,
        ignore_exit_code=True,
    )

    assert res.returncode == 2
    assert "HISTFILE: is read only" in res.stderr
