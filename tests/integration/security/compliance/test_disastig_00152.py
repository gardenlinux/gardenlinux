import pytest
from plugins.shell import ShellRunner


@pytest.mark.feature("stig")
@pytest.mark.booted(reason="requires audit subsystem running")
@pytest.mark.root(reason="required to validate enforcement audit logging")
@pytest.mark.modify(reason="trigger permission denied event")
def test_enforcement_action_audited(shell: ShellRunner, enforcement_test):
    """
    As per DISA STIG compliance requirement, the operating system must audit the
    enforcement actions used to restrict access associated with changes to the system.
    Ref: SRG-OS-000365-GPOS-00152
    """

    FILE_TEST, FILE_TIME = enforcement_test

    shell(f"date '+%H:%M:%S' > {FILE_TIME}")

    shell(
        f"su nobody -s /bin/sh -c 'cat {FILE_TEST}'",
        ignore_exit_code=True,
    )

    audit = shell(
        f'ausearch -ts "$(cat {FILE_TIME})"',
        capture_output=True,
        ignore_exit_code=True,
    )

    stdout = audit.stdout

    assert (
        "EACCES" in stdout or "EPERM" in stdout or "denied" in stdout.lower()
    ), "stigcompliance: enforcement action not audited"
