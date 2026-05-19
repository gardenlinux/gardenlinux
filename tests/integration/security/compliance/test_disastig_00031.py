import pytest

"""
Ref: SRG-OS-000062-GPOS-00031

Verify the operating system provides audit record generation capability for
DoD-defined auditable events for all operating system components.
"""


def test_audit_modify_delete_privileges():
    pytest.skip(reason="covered by test_disastig_00210.py")


def test_audit_modify_delete_security_objects():
    pytest.skip(reason="covered by test_disastig_00212.py")


def test_audit_modify_delete_security_levels():
    pytest.skip(reason="covered by test_disastig_00211.py")


def test_audit_user_access():
    pytest.skip(reason="covered by test_disastig_00220.py")


def test_audit_user_accounts_management():
    pytest.skip(
        reason="covered by test_disastig_00089.py,  test_disastig_00090.py, test_disastig_00091.py"
    )


def test_audit_kernel_module_load_unload():
    pytest.skip(reason="covered by test_disastig_00222.py")
