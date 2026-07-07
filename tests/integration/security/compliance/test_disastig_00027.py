"""
Ref: SRG-OS-000057-GPOS-00027

Verify the operating system protects audit information from unauthorized read
access.
"""

import pytest

AUDIT_LOG_DIR = "/var/log/audit"
AUDIT_LOG_FILE = "/var/log/audit/audit.log"


@pytest.mark.security_id(203616)
@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-audit-log-permissions"])
@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="requires audit subsystem")
@pytest.mark.root(reason="required to inspect audit log permissions")
def test_audit_log_directory_permissions_restricted(file):
    """Verify audit log directory has restrictive permissions (rwx------)."""
    if file.exists(AUDIT_LOG_DIR):
        assert file.has_permissions(
            AUDIT_LOG_DIR, "rwx------"
        ), f"stigcompliance: audit log directory {AUDIT_LOG_DIR} permissions are not restricted"


@pytest.mark.security_id(203616)
@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-audit-log-permissions"])
@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="requires audit subsystem")
@pytest.mark.root(reason="required to inspect audit log permissions")
def test_audit_log_file_permissions_restricted(file):
    """Verify the audit log file has restrictive permissions (rw-------)."""
    if file.exists(AUDIT_LOG_FILE):
        assert file.has_permissions(
            AUDIT_LOG_FILE, "rw-------"
        ), f"stigcompliance: audit log file {AUDIT_LOG_FILE} permissions are not restricted"


@pytest.mark.security_id(203616)
@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-audit-log-permissions"])
@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="requires audit subsystem")
@pytest.mark.root(reason="required to inspect audit log ownership")
def test_audit_log_owned_by_root(file):
    """Verify the audit log file is owned by root."""
    if file.exists(AUDIT_LOG_FILE):
        assert file.is_owned_by_user(
            AUDIT_LOG_FILE, "root"
        ), f"stigcompliance: audit log file {AUDIT_LOG_FILE} is not owned by root"
