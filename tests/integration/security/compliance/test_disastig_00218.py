import pytest
from plugins.shell import ShellRunner

"""
Ref: SRG-OS-000472-GPOS-00218

Verify the operating system generates audit records when concurrent logons to
the same account occur from different sources. 
"""

TEST_USER = "audit_concurrent_user"
OUTPUT_FILE = "/tmp/audit_output_gl.txt"
JOURNAL_FILE = "/tmp/journal_output_gl.txt"
TIME_FILE = "/tmp/audit_start_time"


@pytest.fixture
def concurrent_login_environment(shell: ShellRunner):
    shell(f"id {TEST_USER} || useradd -m {TEST_USER}")
    yield
    shell(f"pkill -9 -u {TEST_USER}", ignore_exit_code=True)
    shell("sleep 1")
    shell(f"userdel -r {TEST_USER}")
    shell(f"rm -f {OUTPUT_FILE} {JOURNAL_FILE} {TIME_FILE}")
    shell(
        "rm -f /etc/group- /etc/gshadow- /etc/passwd- /etc/shadow- /etc/subgid- /etc/subuid-"
    )


@pytest.mark.security_id(203771)
@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="requires kernel logging")
@pytest.mark.root(reason="required to generate audit events")
def test_audit_concurrent_logins(shell: ShellRunner, concurrent_login_environment):
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

    audit_hits = shell(
        f"grep -c '{TEST_USER}' {OUTPUT_FILE}",
        capture_output=True,
        ignore_exit_code=True,
    )
    journal_hits = shell(
        f"grep -c '{TEST_USER}' {JOURNAL_FILE}",
        capture_output=True,
        ignore_exit_code=True,
    )

    total = int(audit_hits.stdout.strip() or 0) + int(journal_hits.stdout.strip() or 0)

    assert (
        total >= 2
    ), "stigcompliance: concurrent login audit events from different sources not detected"
