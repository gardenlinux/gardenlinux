import pytest
from plugins.shell import ShellRunner

OUTPUT_FILE = "/tmp/audit_output_gl.txt"
JOURNAL_FILE = "/tmp/journal_output_gl.txt"
TIME_FILE = "/tmp/audit_start_time"


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="requires kernel logging")
@pytest.mark.root(reason="required to generate audit events")
@pytest.mark.modify(reason="trigger multiple logins for same user for STIG compliance")
def test_audit_concurrent_logins(shell: ShellRunner, temp_user):
    """
    As per DISA STIG compliance requirement, the operating system must generate audit 
    records when concurrent logons to the same account occur from different sources. 
    Ref: SRG-OS-000472-GPOS-00218
    """

    user = temp_user

    shell(f"date '+%H:%M:%S' > {TIME_FILE}")

    shell(f"su - {user} -c 'sleep 30' &")

    shell(
        f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "
        f"{user}@127.0.0.1 'sleep 2' &"
    )

    shell(f'ausearch -ts "$(cat {TIME_FILE})" > {OUTPUT_FILE}')

    shell(
        f'journalctl --since "$(cat {TIME_FILE})" '
        f'| grep -i "{user}" > {JOURNAL_FILE}'
    )

    audit_hits = shell(
        f"grep -c '{user}' {OUTPUT_FILE}", ignore_exit_code=True
    )
    journal_hits = shell(
        f"grep -c '{user}' {JOURNAL_FILE}", ignore_exit_code=True
    )

    audit_count = int((audit_hits.stdout or "").strip() or 0)
    journal_count = int((journal_hits.stdout or "").strip() or 0)

    total = audit_count + journal_count

    assert total >= 2, (
        "stigcompliance: concurrent login audit events from different sources not detected"
    )
