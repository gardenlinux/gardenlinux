"""
Ref: SRG-OS-000470-GPOS-00214

Verify the operating system generates audit records when
successful/unsuccessful logon attempts occur.
"""

import pytest


@pytest.mark.feature("log")
@pytest.mark.booted(reason="Needs running auditd")
@pytest.mark.root(reason="Needs access to audit logs")
def test_audit_record_tools_for_logon_attempts_exist(file):
    """Verify the audit tools aulast and aulastlog are present on the system."""
    assert file.exists("/usr/bin/aulast"), "aulast binary not found"
    assert file.exists("/usr/bin/aulastlog"), "aulastlog binary not found"


@pytest.mark.feature("log")
@pytest.mark.booted(reason="Needs running auditd")
@pytest.mark.root(reason="Needs access to audit logs")
def test_audit_record_tools_for_logon_attempts_function(shell):
    """Verify the aulast tool executes successfully and can query audit records for logon attempts."""
    assert not shell("aulast --proof").returncode
