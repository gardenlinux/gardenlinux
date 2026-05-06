import re

import pytest

"""
Ref: SRG-OS-000358-GPOS-00145

Verify the operating system records time stamps for audit records that meet a
minimum granularity of one second for a minimum degree of precision.
"""


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires audit subsystem running")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_timestamp_granularity(shell):
    result = shell("ausearch -ts recent", capture_output=True)
    timestamp_pattern = r"time->\w{3}\s+\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2}\s+\d{4}"

    assert re.search(
        timestamp_pattern, result.stdout
    ), "stigcompliance: audit records do not contain valid timestamps with second granularity"
