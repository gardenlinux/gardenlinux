import pytest


@pytest.mark.feature("server")
def test_sudo_resets_user_environment(parse_file):
    assert parse_file.has_line("/etc/sudoers", "Defaults env_reset")
