"""
Ref: SRG-OS-000062-GPOS-00031

Verify the operating system provides audit record generation capability for
DoD-defined auditable events for all operating system components.
"""

import pytest


@pytest.mark.security_id(203619)
def test_audit_modify_delete_privileges():
    """Audit of privilege modification/deletion is covered elsewhere."""
    pytest.skip(reason="covered by test_disastig_00210.py")


@pytest.mark.security_id(203619)
def test_audit_modify_delete_security_objects():
    """Audit of security object modification/deletion is covered elsewhere."""
    pytest.skip(reason="covered by test_disastig_00212.py")


@pytest.mark.security_id(203619)
def test_audit_modify_delete_security_levels():
    """Audit of security level modification/deletion is covered elsewhere."""
    pytest.skip(reason="covered by test_disastig_00211.py")


@pytest.mark.security_id(203619)
def test_audit_user_access():
    """Audit of user access events is covered elsewhere."""
    pytest.skip(reason="covered by test_disastig_00220.py")


@pytest.mark.security_id(203619)
def test_audit_user_accounts_management():
    """Audit of user account management is covered elsewhere."""
    pytest.skip(
        reason="covered by test_disastig_00089.py,  test_disastig_00090.py, test_disastig_00091.py"
    )


@pytest.mark.security_id(203619)
def test_audit_kernel_module_load_unload():
    """Audit of kernel module load/unload is covered elsewhere."""
    pytest.skip(reason="covered by test_disastig_00222.py")
