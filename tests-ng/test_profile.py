import pytest
from plugins.parse_file import ParseFile


@pytest.mark.feature("cloud", reason="enabled in cloud feature")
def test_profile_autologout_cloud(parse_file: ParseFile):
    """Test that the autologout profile is set correctly."""
    file = "/etc/profile.d/50-autologout.sh"
    lines_list = [
        "TMOUT=900",
        "readonly TMOUT",
        "export TMOUT",
    ]
    sorted_lines = parse_file.lines(file, ordered=True)
    assert (
        lines_list in sorted_lines
    ), f"Could not find expected lines in order in {file}: {lines_list}"


@pytest.mark.feature("stig", reason="enabled in stig feature")
def test_profile_autologout_stig(parse_file: ParseFile):
    """Test that the autologout profile is set correctly."""
    file = "/etc/profile.d/99-terminal_tmout.sh"
    lines_list = [
        "TMOUT=600",
        "readonly TMOUT",
        "export TMOUT",
    ]
    sorted_lines = parse_file.lines(file, ordered=True)
    assert (
        lines_list in sorted_lines
    ), f"Could not find expected lines in order in {file}: {lines_list}"


@pytest.mark.feature(
    "openstackbaremetal", reason="enabled in openstackbaremetal feature"
)
def test_profile_autologout_openstackbaremetal(parse_file: ParseFile):
    """Test that the autologout profile is set correctly."""
    file = "/etc/profile.d/50-autologout.sh"
    lines_list = [
        "TMOUT=600",
        "readonly TMOUT",
        "export TMOUT",
    ]
    sorted_lines = parse_file.lines(file, ordered=True)
    assert (
        lines_list in sorted_lines
    ), f"Could not find expected lines in order in {file}: {lines_list}"
