import pytest


@pytest.mark.feature("server")
def test_sudo_resets_user_environment(file_content):
    assert file_content.check_line("/etc/sudoers", "Defaults env_reset")
