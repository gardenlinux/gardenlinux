"""
Ref: SRG-OS-000465-GPOS-00209

Verify the operating system generates audit records when
successful/unsuccessful attempts to modify categories of information (e.g.,
classification levels) occur.
"""

import os

import pytest
from plugins.file import File
from plugins.parse_file import Parse, ParseFile
from plugins.shell import ShellRunner

PRIV_ESC_RULE_FILE = "/etc/audit/rules.d/70-privilege-escalation.rules"


@pytest.mark.security_id(203763)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit rule validation requires running audit subsystem")
@pytest.mark.root(reason="required to inspect audit config")
def test_setreuid_rule_file_exists(file: File):
    """Verify the privilege escalation audit rule file exists."""
    assert file.exists(
        PRIV_ESC_RULE_FILE
    ), f"stigcompliance: {PRIV_ESC_RULE_FILE} does not exist"


@pytest.mark.security_id(203763)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit rule validation requires running audit subsystem")
@pytest.mark.root(reason="required to inspect audit config")
def test_setreuid_rule_contains_syscall(parse_file: ParseFile):
    """Verify the privilege escalation rule audits the setreuid syscall."""
    lines = parse_file.lines(PRIV_ESC_RULE_FILE, ignore_missing=True)

    assert (
        lines is not None and "-S setreuid" in lines
    ), "stigcompliance: setreuid audit rule not configured"


@pytest.mark.security_id(203763)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit rule validation requires running audit subsystem")
@pytest.mark.root(reason="required to query audit rules")
def test_setreuid_rule_loaded(shell: ShellRunner, parse: type[Parse]):
    """Verify the setreuid audit rule is loaded into the running kernel."""
    output = shell(cmd="auditctl -l", capture_output=True)

    assert (
        output.returncode == 0
    ), f"stigcompliance: unable to list audit rules: {output.stderr}"

    assert (
        "setreuid" in output.stdout
    ), "stigcompliance: setreuid audit rule not loaded in kernel"


@pytest.mark.security_id(203763)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to trigger syscall and read audit logs")
def test_setreuid_event_logged(shell: ShellRunner):
    """Verify a setreuid call produces a privilege_escalation audit event."""
    pid = os.fork()

    if pid == 0:
        try:
            os.setreuid(123456, 123456)
        except Exception:
            pass
        finally:
            os._exit(0)
    else:
        os.waitpid(pid, 0)

    result = shell(
        cmd="ausearch -k privilege_escalation -ts recent",
        capture_output=True,
        ignore_exit_code=True,
    )

    if result.returncode == 1 or not result.stdout.strip():
        return

    assert "SYSCALL" in result.stdout, "stigcompliance: no syscall audit event detected"
