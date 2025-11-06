import pytest
from plugins.parse_file import FileContent


@pytest.mark.feature("cloud", reason="enabled in cloud feature")
def test_profile_autologout_cloud(file_content: FileContent):
    """Test that the autologout profile is set correctly."""
    file = "/etc/profile.d/50-autologout.sh"
    lines = ["TMOUT=900", "readonly TMOUT", "export TMOUT"]
    result = file_content.check_lines(file, lines)
    assert result, f"Could not find expected lines in order in {file}: {lines}"


@pytest.mark.feature("stig", reason="enabled in stig feature")
def test_profile_autologout_stig(file_content: FileContent):
    """Test that the autologout profile is set correctly."""
    file = "/etc/profile.d/99-terminal_tmout.sh"
    lines = ["TMOUT=600", "readonly TMOUT", "export TMOUT"]
    result = file_content.check_lines(file, lines)
    assert result, f"Could not find expected lines in order in {file}: {lines}"


@pytest.mark.feature(
    "openstackbaremetal", reason="enabled in openstackbaremetal feature"
)
def test_profile_autologout_openstackbaremetal(file_content: FileContent):
    """Test that the autologout profile is set correctly."""
    file = "/etc/profile.d/50-autologout.sh"
    lines = ["TMOUT=600", "readonly TMOUT", "export TMOUT"]
    result = file_content.check_lines(file, lines)
    assert result, f"Could not find expected lines in order in {file}: {lines}"
