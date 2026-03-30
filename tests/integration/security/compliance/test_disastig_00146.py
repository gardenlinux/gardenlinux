import pytest
from plugins.shell import ShellRunner


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires system time configuration")
@pytest.mark.root(reason="required to verify time settings")
def test_audit_timestamp_utc_mapping(shell: ShellRunner, timedatectl):
    """
    As per DISA STIG requirement, the operating system must record audit
    timestamps that can be mapped to UTC or GMT.
    Ref: SRG-OS-000359-GPOS-00146
    """
    result = shell(
        "timedatectl show -p Timezone",
        capture_output=True,
        ignore_exit_code=True,
    )

    timezone = result.stdout.strip().split("=")[-1]

    assert timezone, "stigcompliance: timezone not configured"

    assert (
        "UTC" in timezone or "GMT" in timezone or "/" in timezone
    ), f"stigcompliance: timezone not mappable to UTC/GMT: {timezone}"
