"""
Ref: SRG-OS-000480-GPOS-00226

Verify the operating system enforces a delay of at least 4 seconds between
logon prompts following a failed logon attempt.
"""

import pytest


@pytest.mark.security_id(203779)
@pytest.mark.parametrize("pam_config", ["/etc/pam.d/login"], indirect=["pam_config"])
@pytest.mark.feature("disaSTIGmedium")
def test_delay_is_enforced_after_failed_logins(pam_config):
    """Verify pam_faildelay enforces a 4-second delay in /etc/pam.d/login."""
    results = pam_config.find_entries(
        type_="auth",
        control_contains="required",
        module_contains="pam_faildelay.so",
        arg_contains="delay=4000000",  # microseconds, 4 * 1mln
    )
    assert len(results) == 1, "pam_faildelay should enforce a delay of 4 seconds"
