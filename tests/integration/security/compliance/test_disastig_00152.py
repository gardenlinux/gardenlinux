import pytest
from plugins.shell import ShellRunner


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="requires audit subsystem running")
@pytest.mark.root(reason="required to validate enforcement audit logging")
def test_enforcement_action_audited(shell: ShellRunner):
    """
    As per DISA STIG compliance requirement, the operating system must audit the
    enforcement actions used to restrict access associated with changes to the system.
    Ref: SRG-OS-000365-GPOS-00152
    """

    shell(
        "su nobody -s /bin/sh -c 'cat /etc/shadow'",
        ignore_exit_code=True,
    )

    audit = shell(
        "ausearch -ts recent",
        capture_output=True,
        ignore_exit_code=True,
    )

    stdout = audit.stdout or ""

    assert (
        "EACCES" in stdout or "EPERM" in stdout or "denied" in stdout.lower()
    ), f"stigcompliance: enforcement action not audited; ausearch output: {stdout[:200]}"
