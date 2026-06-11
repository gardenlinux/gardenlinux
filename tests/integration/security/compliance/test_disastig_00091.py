"""
Ref: SRG-OS-000241-GPOS-00091

Verify the operating system automatically audits account removal actions.
"""

import pytest


@pytest.mark.security_id(203668)
def test_disastig_00091():
    """Auditing of account removal actions is covered elsewhere."""
    pytest.skip(reason="covered by test_disastig_00089.py")


@pytest.mark.security_id(203668)
def test_audit_rules_for_logging_attempts_to_delete_privileges():
    """Audit rules for privilege deletion are covered elsewhere."""
    pytest.skip(
        reason="covered by test_disastig_00210::test_audit_rules_for_logging_attempts_to_delete_privileges"
    )
