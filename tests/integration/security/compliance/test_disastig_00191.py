import time

import pytest
from plugins.shell import ShellRunner

"""
Ref: SRG-OS-000432-GPOS-00191

Verify the operating system behaves in a predictable and documented manner that
reflects organizational and system objectives when invalid inputs are received.
"""


@pytest.mark.security_id(203752)
@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="requires audit subsystem running")
@pytest.mark.root(reason="useradd and ausearch require root privileges")
@pytest.mark.modify(reason="creates and removes a temporary user account")
def test_invalid_input_handling_is_audited(shell: ShellRunner, audit_user):
    """Verify ausearch -ts recent output contains name="/etc/shadow"."""
    shell(f"su {audit_user} -c 'echo >> /etc/shadow'", ignore_exit_code=True)
    time.sleep(1)
    result = shell(cmd="ausearch -ts recent", capture_output=True)

    assert (
        'name="/etc/shadow"' in result.stdout
    ), "stigcompliance: no failed-syscall audit event found after trying to write to a system file"
