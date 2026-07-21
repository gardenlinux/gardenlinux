"""
Ref: SRG-OS-000051-GPOS-00024

Verify the operating system provides the capability to centrally review and
analyze audit records from multiple components within the system.
"""

import re

import pytest

AUDITD_CONF = "/etc/audit/auditd.conf"


@pytest.mark.security_id(203613)
@pytest.mark.feature("not container and not lima")
@pytest.mark.root(reason="required to read audit configuration")
def test_audit_log_retention_config(parse_file):
    """Verify auditd.conf defines max_log_file, num_logs and space_left_action."""
    lines = parse_file.lines(AUDITD_CONF)

    assert (
        re.compile(r"max_log_file\s*=\s*\d+") in lines
    ), "stigcompliance: max_log_file not configured properly"

    assert (
        re.compile(r"num_logs\s*=\s*\d+") in lines
    ), "stigcompliance: num_logs not configured properly"

    assert (
        re.compile(r"space_left_action\s*=\s*\S+") in lines
    ), "stigcompliance: space_left_action not configured"


@pytest.mark.security_id(203613)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit retention validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit configuration and logs")
def test_audit_log_retention_availability(shell):
    """Verify ausearch returns structured audit records (retention works)."""
    result = shell("ausearch -ts recent", capture_output=True)
    returncode = result.returncode
    has_output = result.stdout.strip() != ""
    has_structured = "type=" in result.stdout

    assert (
        returncode == 0
    ), "stigcompliance: ausearch failed, audit logs not retrievable"
    assert has_output, "stigcompliance: no audit records found (retention failure)"
    assert (
        has_structured
    ), "stigcompliance: audit records not in expected structured format"
