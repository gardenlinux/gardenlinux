import re

import pytest

"""
Ref: SRG-OS-000055-GPOS-00026

Verify the operating system uses internal system clocks to generate time stamps
for audit records.
"""


@pytest.mark.feature("stig")
@pytest.mark.booted(reason="requires audit subsystem running")
@pytest.mark.root(reason="required to generate and read audit logs")
def test_audit_records_have_valid_timestamps(shell):
    result = shell("ausearch -ts recent", capture_output=True)

    timestamp_pattern = r"time->\w{3}\s+\w{3}\s+\d+\s+\d+:\d+:\d+\s+\d{4}"

    assert re.search(
        timestamp_pattern, result.stdout
    ), "stigcompliance: audit records do not contain valid timestamps"


@pytest.mark.feature("stig")
@pytest.mark.booted(reason="requires audit subsystem running")
@pytest.mark.root(reason="required to generate and read audit logs")
def test_system_time_status_available(shell):
    timedate = shell("timedatectl status", capture_output=True)

    assert timedate.returncode == 0, "stigcompliance: unable to check time sync status"
