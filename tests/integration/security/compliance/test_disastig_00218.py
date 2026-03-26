import pytest
from plugins.shell import ShellRunner

TEST_USER = "audit_concurrent_user"
OUTPUT_FILE = "/tmp/audit_output_gl.txt"
JOURNAL_FILE = "/tmp/journal_output_gl.txt"
TIME_FILE = "/tmp/audit_start_time"


@pytest.fixture
def concurrent_login_environment(shell: ShellRunner):
    """
    As per DISA STIG compliance requirement, the operating system must generate audit
    records when concurrent logons to the same account occur from different sources.
    Ref: SRG-OS-000472-GPOS-00218
    """
    shell(f"id {TEST_USER} || useradd -m {TEST_USER}")
    yield
    shell(f"pkill -u {TEST_USER}")
    shell(f"userdel -r {TEST_USER}")
    shell(f"rm -f {OUTPUT_FILE} {JOURNAL_FILE} {TIME_FILE}")


@pytest.mark.feature("stig")
@pytest.mark.booted(reason="requires kernel logging")
@pytest.mark.root(reason="required to generate audit events")
def test_audit_concurrent_logins(shell: ShellRunner, concurrent_login_environment):
    """
    As per DISA STIG compliance requirement, the operating system must generate audit
    records when concurrent logons to the same account occur from different sources.
    Ref: SRG-OS-000472-GPOS-00218
    """
    shell(f"date '+%H:%M:%S' > {TIME_FILE}")

    shell(f"su - {TEST_USER} -c 'sleep 30' &")

    shell(
        f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "
        f"{TEST_USER}@127.0.0.1 'sleep 30' &"
    )

    shell("sleep 5")

    shell(f'ausearch -ts "$(cat {TIME_FILE})" > {OUTPUT_FILE}')

    shell(
        f'journalctl --since "$(cat {TIME_FILE})" '
        f'| grep -i "{TEST_USER}" > {JOURNAL_FILE}'
    )

    audit_hits = shell(f"grep -c '{TEST_USER}' {OUTPUT_FILE}")
    journal_hits = shell(f"grep -c '{TEST_USER}' {JOURNAL_FILE}")

    total = int(audit_hits.stdout.strip() or 0) + int(journal_hits.stdout.strip() or 0)

    assert (
        total >= 2
    ), "stigcompliance: concurrent login audit events from different sources not detected"
