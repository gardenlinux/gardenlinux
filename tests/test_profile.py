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

@pytest.mark.feature("stig", reason="enabled in stig feature")
def test_shell_inactivity_timeout_stig(parse_file: ParseFile):
    """
    Validate that an inactivity timeout is enforced for shell sessions
    via TMOUT configuration.
    """
    file = "/etc/profile.d/99-terminal_tmout.sh"

    # Configuration must exist
    assert parse_file.exists(file), (
        "compliance: shell inactivity timeout configuration file is missing"
    )

    lines = parse_file.lines(file)

    lines_list = [
        line.strip()
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    ]

    # TMOUT must be set to a finite value
    tmout_lines = [
        line for line in lines_list
        if re.fullmatch(r"TMOUT\s*=\s*\d+", line)
    ]

    assert tmout_lines, "compliance: TMOUT is not configured"

    # Ensure TMOUT is protected and applied
    assert "readonly TMOUT" in lines_list, (
        "compliance: TMOUT is not marked as readonly"
    )

    assert "export TMOUT" in lines_list, (
        "compliance: TMOUT is not exported"
    )
