import re

import pytest
from plugins.parse_file import ParseFile


@pytest.mark.testcov(["GL-TESTCOV-cloud-script-profile-autologout"])
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


# TODO: decide if "stig" feature shall get more setting/test
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


@pytest.mark.testcov(["GL-TESTCOV-openstackMetal-script-profile-autologout"])
@pytest.mark.feature(
    "openstack and metal", reason="enabled in openstack on metal feature"
)
def test_profile_autologout_openstack_metal(parse_file: ParseFile):
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


TMOUT_FILE_STIG = "/etc/profile.d/99-terminal_tmout.sh"


@pytest.mark.feature("stig")
def test_shell_tmout_file_exists_stig(parse_file: ParseFile):
    """
    As per DISA STIG requirement, this test validates that the shell inactivity
    timeout configuration file exists.
    Ref: SRG-OS-000755-GPOS-00220
    """
    assert parse_file.exists(
        TMOUT_FILE_STIG
    ), "stigcompliance: shell inactivity timeout configuration file is missing"


@pytest.mark.feature("stig")
def test_shell_tmout_is_configured_stig(parse_file: ParseFile):
    """
    As per DISA STIG requirement, this test verifies that TMOUT variable is configured.
    Ref: SRG-OS-000755-GPOS-00220
    """
    assert re.compile(r"TMOUT\s*=\s*\d+") in parse_file.lines(
        TMOUT_FILE_STIG
    ), "stigcompliance: TMOUT is not configured"


@pytest.mark.feature("stig")
def test_shell_tmout_is_readonly_stig(parse_file: ParseFile):
    """
    As per DISA STIG requirement, this test verifies that TMOUT is marked ReadOnly.
    Ref: SRG-OS-000755-GPOS-00220
    """
    assert re.compile(r"readonly\s+TMOUT") in parse_file.lines(
        TMOUT_FILE_STIG
    ), "stigcompliance: TMOUT is not marked as readonly"


@pytest.mark.feature("stig")
def test_shell_tmout_is_exported_stig(parse_file: ParseFile):
    """
    As per DISA STIG requirement, this test verifies that TMOUT is
    exported to subshells.
    Ref: SRG-OS-000755-GPOS-00220
    """
    assert re.compile(r"export\s+TMOUT") in parse_file.lines(
        TMOUT_FILE_STIG
    ), "stigcompliance: TMOUT is not exported"


TMOUT_FILE_CLOUD = "/etc/profile.d/50-autologout.sh"


@pytest.mark.feature("cloud and openstack and metal")
def test_shell_tmout_file_exists_cloud(parse_file: ParseFile):
    """
    As per DISA STIG requirement, this test validates that the shell inactivity
    timeout configuration file exists.
    Ref: SRG-OS-000755-GPOS-00220
    """
    assert parse_file.exists(
        TMOUT_FILE_CLOUD
    ), "stigcompliance: shell inactivity timeout configuration file is missing"


@pytest.mark.feature("cloud and openstack and metal")
def test_shell_tmout_is_configured_cloud(parse_file: ParseFile):
    """
    As per DISA STIG requirement, this test verifies that TMOUT variable is configured.
    Ref: SRG-OS-000755-GPOS-00220
    """
    assert re.compile(r"TMOUT\s*=\s*\d+") in parse_file.lines(
        TMOUT_FILE_CLOUD
    ), "stigcompliance: TMOUT is not configured"


@pytest.mark.feature("cloud and openstack and metal")
def test_shell_tmout_is_readonly_cloud(parse_file: ParseFile):
    """
    As per DISA STIG requirement, this test verifies that TMOUT is marked ReadOnly.
    Ref: SRG-OS-000755-GPOS-00220
    """
    assert re.compile(r"readonly\s+TMOUT") in parse_file.lines(
        TMOUT_FILE_CLOUD
    ), "stigcompliance: TMOUT is not marked as readonly"


@pytest.mark.feature("cloud and openstack and metal")
def test_shell_tmout_is_exported_cloud(parse_file: ParseFile):
    """
    As per DISA STIG requirement, this test verifies that TMOUT is
    exported to subshells.
    Ref: SRG-OS-000755-GPOS-00220
    """
    assert re.compile(r"export\s+TMOUT") in parse_file.lines(
        TMOUT_FILE_CLOUD
    ), "stigcompliance: TMOUT is not exported"
