import pytest
from plugins.parse_file import ParseFile
from plugins.shell import ShellRunner

PRIV_ESC_RULE_FILE = "/etc/audit/rules.d/70-privilege-escalation.rules"


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit rule validation requires running audit subsystem")
@pytest.mark.root(reason="required to query audit logs")
def test_setreuid_rule_file_exists(parse_file: ParseFile):
    """
    As per DISA STIG requirement, the operating system must generate audit
    records when successful or unsuccessful attempts to modify categories
    of information occur (e.g., privilege changes such as setreuid).
    This test verifies that the audit subsystem is capable of searching
    for events associated with the configured audit key for privilege
    escalation.
    Ref: SRG-OS-000465-GPOS-00209
    """
    lines = parse_file.lines(PRIV_ESC_RULE_FILE, ignore_missing=True)

    assert (
        lines is not None
    ), "stigcompliance: privilege escalation audit rule file missing"


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit rule validation requires running audit subsystem")
@pytest.mark.root(reason="required to query audit logs")
def test_setreuid_rule_contains_syscall(parse_file: ParseFile):
    """
    As per DISA STIG requirement, the operating system must generate audit
    records when successful or unsuccessful attempts to modify categories
    of information occur (e.g., privilege changes such as setreuid).
    This test verifies that the audit subsystem is capable of searching
    for events associated with the configured audit key for privilege
    escalation.
    Ref: SRG-OS-000465-GPOS-00209
    """
    lines = parse_file.lines(PRIV_ESC_RULE_FILE, ignore_missing=True)

    assert "-S setreuid" in lines, "stigcompliance: setreuid audit rule not configured"


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit rule validation requires running audit subsystem")
@pytest.mark.root(reason="required to query audit logs")
def test_setreuid_rule_loaded(shell: ShellRunner):
    """
    As per DISA STIG requirement, the operating system must generate audit
    records when successful or unsuccessful attempts to modify categories
    of information occur (e.g., privilege changes such as setreuid).
    This test verifies that the audit subsystem is capable of searching
    for events associated with the configured audit key for privilege
    escalation.
    Ref: SRG-OS-000465-GPOS-00209
    """
    output = shell(cmd="auditctl -l", capture_output=True)

    assert (
        output.returncode == 0
    ), f"stigcompliance: unable to list audit rules: {output.stderr}"

    assert (
        "setreuid" in output.stdout
    ), "stigcompliance: setreuid audit rule not loaded in kernel"


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit rule validation requires running audit subsystem")
@pytest.mark.root(reason="required to query audit logs")
def test_setreuid_audit_search(shell: ShellRunner):
    """
    As per DISA STIG requirement, the operating system must generate audit
    records when successful or unsuccessful attempts to modify categories
    of information occur (e.g., privilege changes such as setreuid).
    This test verifies that the audit subsystem is capable of searching
    for events associated with the configured audit key for privilege
    escalation.
    Ref: SRG-OS-000465-GPOS-00209
    """
    output = shell(
        cmd="ausearch -k privilege_escalation -sc setreuid",
        capture_output=True,
    )

    assert (
        output.returncode == 0
    ), f"stigcompliance: unable to search audit records for setreuid: {output.stderr}"
