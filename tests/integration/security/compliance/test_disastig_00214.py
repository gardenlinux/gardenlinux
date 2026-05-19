import pytest

"""
Ref: SRG-OS-000470-GPOS-00214

Verify the operating system generates audit records when
successful/unsuccessful logon attempts occur.
"""


@pytest.mark.feature("log")
@pytest.mark.root(reason="Needs access to audit logs")
def test_audit_record_tools_for_logon_attempts_exist(file):
    assert file.exists("/usr/bin/aulast"), "aulast binary not found"
    assert file.exists("/usr/bin/aulastlog"), "aulastlog binary not found"


@pytest.mark.feature("log")
@pytest.mark.root(reason="Needs access to audit logs")
def test_audit_record_tools_for_logon_attempts_function(shell):
    assert not shell("aulast --proof").returncode
