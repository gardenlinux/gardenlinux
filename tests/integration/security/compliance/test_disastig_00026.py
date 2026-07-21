"""
Ref: SRG-OS-000055-GPOS-00026

Verify the operating system uses internal system clocks to generate time stamps
for audit records.
"""

import re

import pytest


@pytest.mark.security_id(203615)
@pytest.mark.feature("stig")
@pytest.mark.booted(reason="requires audit subsystem running")
@pytest.mark.root(reason="required to generate and read audit logs")
def test_audit_records_have_valid_timestamps(shell):
    """Verify ausearch -ts recent output contains a 'time->' line in the expected date format."""
    result = shell("ausearch -ts recent", capture_output=True)
    timestamp_pattern = r"time->\w{3}\s+\w{3}\s+\d+\s+\d+:\d+:\d+\s+\d{4}"
    has_timestamp = bool(re.search(timestamp_pattern, result.stdout))
    assert (
        has_timestamp
    ), "stigcompliance: audit records do not contain valid timestamps"


@pytest.mark.security_id(203615)
@pytest.mark.feature("stig")
@pytest.mark.booted(reason="requires audit subsystem running")
@pytest.mark.root(reason="required to generate and read audit logs")
def test_system_time_status_available(shell):
    """Verify timedatectl status exits 0."""
    timedate = shell("timedatectl status", capture_output=True)
    returncode = timedate.returncode
    assert returncode == 0, "stigcompliance: unable to check time sync status"
