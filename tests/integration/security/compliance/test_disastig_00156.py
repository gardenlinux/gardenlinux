import glob

import pytest


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.root(reason="requires access to sudoers configuration")
def test_sudoers_no_nopasswd_or_authenticate_bypass():
    """
    As per DISA STIG compliance requirements, the operating system must require
    users to reauthenticate for privilege escalation.
    This test verifies that sudoers configuration does not contain NOPASSWD
    or !authenticate directives that would bypass authentication.
    Ref: SRG-OS-000373-GPOS-00156
    """
    sudoers_files = ["/etc/sudoers"] + glob.glob("/etc/sudoers.d/*")
    violations = []

    for path in sudoers_files:
        try:
            with open(path) as f:
                for lineno, line in enumerate(f, start=1):
                    stripped = line.strip()
                    if stripped.startswith("#"):
                        continue
                    lower = stripped.lower()
                    if "nopasswd" in lower or "!authenticate" in lower:
                        violations.append(f"{path}:{lineno}: {stripped}")
        except (FileNotFoundError, IsADirectoryError):
            continue

    assert not violations, (
        "stigcompliance: sudoers contains NOPASSWD or !authenticate directives:\n"
        + "\n".join(violations)
    )
