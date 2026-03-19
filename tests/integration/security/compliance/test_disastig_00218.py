import pytest
from plugins.shell import ShellRunner

TEST_USER = "audit_concurrent_user"
OUTPUT_FILE = "/tmp/audit_output_gl.txt"
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
    shell(f"rm -f {OUTPUT_FILE} {TIME_FILE}")


@pytest.mark.feature(
    "not container and not gardener and not lima and not capi and not baremetal"
)
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
    shell(f"su - {TEST_USER} -c 'sleep 30' &")

    shell("sleep 3")

    shell(f'ausearch -m USER_START -ts "$(cat {TIME_FILE})" > {OUTPUT_FILE}')

    result = shell(f"grep -q 'acct=\"{TEST_USER}\"' {OUTPUT_FILE}")

    assert (
        result.returncode == 0
    ), "stigcompliance: concurrent login audit event not detected"
