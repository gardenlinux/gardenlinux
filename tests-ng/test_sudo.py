import pytest
from plugins.parse_file import ParseFile


@pytest.mark.feature("server")
def test_sudo_resets_user_environment(parse_file: ParseFile):
    lines = parse_file.lines("/etc/sudoers")
    assert "Defaults env_reset" in lines
