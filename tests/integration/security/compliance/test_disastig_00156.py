"""
Ref: SRG-OS-000373-GPOS-00156

Verify the operating system requires users to reauthenticate for privilege
escalation. The sudoers wheel file must exist and be empty so that wheel-group
membership does not grant passwordless sudo. No sudoers file may grant
passwordless privilege escalation via NOPASSWD or bypass authentication
via !authenticate.
"""

import re

import pytest
from plugins.find import Find
from plugins.parse_file import ParseFile

SUDOERS_WHEEL = "/etc/sudoers.d/wheel"


@pytest.mark.feature(
    "disaSTIGmedium and not _dev",
    reason="test runner injects NOPASSWD sudoers in _dev mode for SSH access",
)
@pytest.mark.security_id(203723)
@pytest.mark.root(reason="requires access to /etc/sudoers and /etc/sudoers.d")
def test_sudoers_no_nopasswd(find: Find, parse_file: ParseFile):
    """Verify no sudoers file enables NOPASSWD."""
    nopasswd_pattern = re.compile(r"NOPASSWD", re.IGNORECASE)

    find.root_paths = "/etc/sudoers.d"
    find.entry_type = "files"
    paths_to_check = ["/etc/sudoers"] + list(find)

    for path in paths_to_check:
        lines = parse_file.lines(path, ignore_missing=True)
        if not lines:
            continue
        matches = nopasswd_pattern.findall(lines.content)
        assert not matches, f"stigcompliance: NOPASSWD found in sudoers file {path}"


@pytest.mark.feature(
    "disaSTIGmedium and not _dev",
    reason="test runner injects NOPASSWD sudoers in _dev mode for SSH access",
)
@pytest.mark.security_id(203723)
@pytest.mark.root(reason="requires access to /etc/sudoers and /etc/sudoers.d")
def test_sudoers_no_authenticate_bypass(find: Find, parse_file: ParseFile):
    """Verify no sudoers file uses !authenticate to bypass password prompts."""
    noauthenticate_pattern = re.compile(r"!authenticate", re.IGNORECASE)

    find.root_paths = "/etc/sudoers.d"
    find.entry_type = "files"
    paths_to_check = ["/etc/sudoers"] + list(find)

    for path in paths_to_check:
        lines = parse_file.lines(path, ignore_missing=True)
        if not lines:
            continue
        matches = noauthenticate_pattern.findall(lines.content)
        assert (
            not matches
        ), f"stigcompliance: !authenticate found in sudoers file {path}"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-sudoers-wheel"])
@pytest.mark.feature(
    "disaSTIGmedium", reason="sudoers wheel truncation is applied by disaSTIGmedium"
)
@pytest.mark.security_id(203723)
def test_sudoers_wheel_file_exists(file) -> None:
    """Verify /etc/sudoers.d/wheel exists (created/truncated by disaSTIGmedium)."""
    assert file.exists(SUDOERS_WHEEL), f"stigcompliance: {SUDOERS_WHEEL} does not exist"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-sudoers-wheel"])
@pytest.mark.feature(
    "disaSTIGmedium", reason="sudoers wheel truncation is applied by disaSTIGmedium"
)
@pytest.mark.security_id(203723)
def test_sudoers_wheel_file_is_empty(file) -> None:
    """Verify /etc/sudoers.d/wheel is empty (disaSTIGmedium truncates it with echo -n)."""
    assert (
        file.get_size(SUDOERS_WHEEL) == 0
    ), f"stigcompliance: {SUDOERS_WHEEL} is not empty (size={file.get_size(SUDOERS_WHEEL)})"
