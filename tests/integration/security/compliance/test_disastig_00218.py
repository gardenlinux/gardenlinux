"""
Ref: SRG-OS-000472-GPOS-00218

Verify the operating system generates audit records when concurrent logons to
the same account occur from different sources.
"""

import tempfile

import pytest
from handlers.audit_user import TEST_USER
from plugins.shell import ShellRunner


@pytest.mark.security_id(203771)
@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="requires kernel logging")
@pytest.mark.root(reason="required to generate audit events")
@pytest.mark.modify(reason="creates and removes a temporary user account")
def test_audit_concurrent_logins(shell: ShellRunner, audit_user):
    """Verify a su login plus an ssh login for the same user produce >=2 hits in ausearch and journalctl combined."""
    with tempfile.TemporaryDirectory() as tmp:
        time_file = f"{tmp}/audit_start_time"
        output_file = f"{tmp}/audit_output_gl.txt"
        journal_file = f"{tmp}/journal_output_gl.txt"

        shell(f"date '+%H:%M:%S' > {time_file}")

        shell(f"su - {TEST_USER} -c 'sleep 30' &")

        shell(
            f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "
            f"{TEST_USER}@127.0.0.1 'sleep 30' &"
        )

        shell("sleep 5")

        shell(f'ausearch -ts "$(cat {time_file})" > {output_file}')

        shell(
            f'journalctl --since "$(cat {time_file})" '
            f'| grep -i "{TEST_USER}" > {journal_file}'
        )

        audit_hits = shell(
            f"grep -c '{TEST_USER}' {output_file}",
            capture_output=True,
            ignore_exit_code=True,
        )
        journal_hits = shell(
            f"grep -c '{TEST_USER}' {journal_file}",
            capture_output=True,
            ignore_exit_code=True,
        )

        total = int(audit_hits.stdout.strip() or 0) + int(
            journal_hits.stdout.strip() or 0
        )

    assert (
        total >= 2
    ), "stigcompliance: concurrent login audit events from different sources not detected"
