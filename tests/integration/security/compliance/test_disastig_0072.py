import pytest

"""
Ref: SRG-OS-000163-GPOS-00072

Verify the operating system terminates all network connections associated with
a communications session at the end of the session, or as follows: for in-band
management sessions (privileged sessions), the session must be terminated after
10 minutes of inactivity; and for user sessions (non-privileged session), the
session must be terminated after 15 minutes of inactivity, except to fulfill
documented and validated mission requirements.
"""


@pytest.mark.feature("ssh")
def test_terminate_ssh_session_after_inactivity_period(parse_file):
    config = parse_file.parse("/etc/ssh/sshd_config", format="spacedelim")
    assert config["ClientAliveInterval"] == "600"
    assert config["ClientAliveCountMax"] == "1"
