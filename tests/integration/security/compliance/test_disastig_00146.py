import pytest
from plugins.shell import ShellRunner

"""
Ref: SRG-OS-000359-GPOS-00146

Verify the operating system records time stamps for audit records that can be
mapped to Coordinated Universal Time (UTC) or Greenwich Mean Time (GMT).
"""


@pytest.mark.security_id(203714)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires system time configuration")
@pytest.mark.root(reason="required to verify time settings")
def test_audit_timestamp_utc_mapping(shell: ShellRunner, timedatectl):
    result = shell(
        "timedatectl show -p Timezone",
        capture_output=True,
        ignore_exit_code=True,
    )

    timezone = result.stdout.strip().split("=")[-1]

    assert timezone, "stigcompliance: timezone not configured"

    assert (
        "UTC" in timezone or "GMT" in timezone
    ), f"stigcompliance: timezone not mappable to UTC/GMT: {timezone}"
