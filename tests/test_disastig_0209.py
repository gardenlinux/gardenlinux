import time

import pytest
from plugins.file import File
from plugins.parse_file import Parse, ParseFile
from plugins.shell import ShellRunner

PRIV_ESC_RULE_FILE = "/etc/audit/rules.d/70-privilege-escalation.rules"
TEST_USER = "audit_test_user"


@pytest.fixture
def audit_test_user(shell: ShellRunner):
    """
    As per DISA STIG requirement, the operating system must generate audit
    records when successful or unsuccessful attempts to modify categories
    of information occur (e.g., privilege changes such as setreuid).
    This test verifies that the audit subsystem is capable of searching
    for events associated with the configured audit key for privilege
    escalation.
    Ref: SRG-OS-000465-GPOS-00209
    """
    shell(cmd=f"useradd {TEST_USER}")
    yield TEST_USER
    shell(cmd=f"userdel -fr {TEST_USER}")


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit rule validation requires running audit subsystem")
@pytest.mark.root(reason="required to query audit logs")
def test_setreuid_rule_file_exists(file: File):
    """
    As per DISA STIG requirement, the operating system must generate audit
    records when successful or unsuccessful attempts to modify categories
    of information occur (e.g., privilege changes such as setreuid).
    This test verifies that the audit subsystem is capable of searching
    for events associated with the configured audit key for privilege
    escalation.
    Ref: SRG-OS-000465-GPOS-00209
    """
    assert file.exists(PRIV_ESC_RULE_FILE), f"'{PRIV_ESC_RULE_FILE}' does not exist"


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
def test_setreuid_rule_loaded(shell: ShellRunner, parse: type[Parse]):
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
@pytest.mark.modify(reason="creates temporary user and modifies system state")
def test_setreuid_event_logged(shell: ShellRunner, audit_test_user: str):
    """
    As per DISA STIG requirement, the operating system must generate audit
    records when successful or unsuccessful attempts to modify categories
    of information occur (e.g., privilege changes such as setreuid).
    This test verifies that the audit subsystem is capable of searching
    for events associated with the configured audit key for privilege
    escalation.
    Ref: SRG-OS-000465-GPOS-00209
    """

    shell(cmd=f"su - {TEST_USER} -c 'id'")

    time.sleep(1)

    result = shell(
        cmd="ausearch -sc setreuid -ts recent",
        capture_output=True,
    )

    assert result.stdout.strip(), "stigcompliance: setreuid audit event not detected"
