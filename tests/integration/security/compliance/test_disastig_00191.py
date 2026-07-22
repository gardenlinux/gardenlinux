"""
Ref: SRG-OS-000432-GPOS-00191

Verify the operating system behaves in a predictable and documented manner that
reflects organizational and system objectives when invalid inputs are received.
"""

# TODO: fix in https://github.com/gardenlinux/gardenlinux/pull/5036
# import pytest
#
#
# @pytest.mark.security_id(203752)
# @pytest.mark.feature("not container and not lima")
# @pytest.mark.booted(reason="requires audit subsystem running")
# @pytest.mark.root(reason="required to read audit logs")
# def test_invalid_input_handling_is_audited(shell):
#     """Verify ausearch -ts recent output contains 'success=no', 'res=failed' or 'invalid'."""
#     result = shell("ausearch -ts recent", capture_output=True)
#     stdout = result.stdout
#
#     assert (
#         "success=no" in stdout or "res=failed" in stdout or "invalid" in stdout.lower()
#     ), "stigcompliance: audit records do not contain evidence of handling invalid inputs"
