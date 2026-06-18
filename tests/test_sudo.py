import pytest
from plugins.parse_file import ParseFile


@pytest.mark.feature("server")
def test_sudo_secure_path_is_set(parse_file: ParseFile):
    lines = parse_file.lines("/etc/sudoers")
    assert "Defaults secure_path" in lines
