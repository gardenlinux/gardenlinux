"""
Ref: SRG-OS-000358-GPOS-00145

Verify the operating system records time stamps for audit records that meet a
minimum granularity of one second for a minimum degree of precision.
"""

import re

import pytest


@pytest.mark.security_id(203713)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires audit subsystem running")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_timestamp_granularity(shell):
    """Verify audit timestamps have at least one-second granularity."""
    result = shell("ausearch -ts recent", capture_output=True)
    timestamp_pattern = r"time->\w{3}\s+\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2}\s+\d{4}"
    has_timestamp = bool(re.search(timestamp_pattern, result.stdout))
    assert has_timestamp, "stigcompliance: audit records do not contain valid timestamps with second granularity"
