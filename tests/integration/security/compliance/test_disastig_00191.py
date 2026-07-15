import pytest

"""
Ref: SRG-OS-000432-GPOS-00191

Verify the operating system behaves in a predictable and documented manner that
reflects organizational and system objectives when invalid inputs are received.
"""


@pytest.mark.security_id(203752)
@pytest.mark.feature("log")
@pytest.mark.booted(reason="requires audit subsystem running")
def test_invalid_input_handling_is_audited(shell):
    shell("echo '# test' >> /root/.profile", ignore_exit_code=True)
    result = shell(cmd="ausearch -ts recent", capture_output=True)

    assert "success=no" in result.stdout(
        "stigcompliance: no failed-syscall audit event found after triggering EACCES via openat"
    )
