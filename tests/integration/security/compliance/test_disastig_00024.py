import re

import pytest

"""
Ref: SRG-OS-000051-GPOS-00024

Verify the operating system provides the capability to centrally review and
analyze audit records from multiple components within the system.
"""

AUDITD_CONF = "/etc/audit/auditd.conf"


@pytest.mark.security_id(203613)
@pytest.mark.feature("not container and not lima")
@pytest.mark.root(reason="required to read audit configuration")
def test_audit_log_retention_config(parse_file):
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
    result = shell("ausearch -ts recent", capture_output=True)

    assert (
        result.returncode == 0
    ), "stigcompliance: ausearch failed, audit logs not retrievable"

    output = result.stdout.strip()

    assert output != "", "stigcompliance: no audit records found (retention failure)"

    assert (
        "type=" in output
    ), "stigcompliance: audit records not in expected structured format"
