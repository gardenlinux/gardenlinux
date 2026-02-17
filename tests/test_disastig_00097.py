import os
import stat

import pytest

# Global paths for audit tools
AUDIT_TOOL_PATHS = [
    "/sbin/auditctl",
    "/usr/sbin/auditctl",
    "/usr/bin/last",
    "/usr/bin/journalctl",
]

AUDIT_LOG_FILE = "/var/log/audit/audit.log"


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_auditctl_owned_by_root():
    """
    As per DISA STIG requirement, we have to ensure that only the root user is allowed
    to access the audit tools like auditctl, last (wtmpdb) and journalctl. This should
    be applied for the operating system only, but not for containers.
    Ref: SRG-OS-000256-GPOS-00097
    """

    for path in AUDIT_TOOL_PATHS:
        if os.path.exists(path):
            info = os.stat(path)
            assert info.st_uid == 0, f"stigcompliance: {path} not owned by root"


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_auditctl_not_world_writable():
    """
    As per DISA STIG requirement, we have to ensure that only the root user is allowed
    to access the audit tools like auditctl, last (wtmpdb) and journalctl. This should
    be applied for the operating system only, but not for containers.
    Ref: SRG-OS-000256-GPOS-00097
    """

    for path in AUDIT_TOOL_PATHS:
        if os.path.exists(path):
            info = os.stat(path)
            assert not (
                info.st_mode & stat.S_IWOTH
            ), f"stigcompliance: {path} is world-writable"


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_auditctl_not_group_writable():
    """
    As per DISA STIG requirement, we have to ensure that only the root user is allowed
    to access the audit tools like auditctl, last (wtmpdb) and journalctl. This should
    be applied for the operating system only, but not for containers.
    Ref: SRG-OS-000256-GPOS-00097
    """

    for path in AUDIT_TOOL_PATHS:
        if os.path.exists(path):
            info = os.stat(path)
            assert not (
                info.st_mode & stat.S_IWGRP
            ), f"stigcompliance: {path} is group-writable"

@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_audit_log_owned_by_root():
    """
    As per DISA STIG requirement, we have to ensure that only the root user is allowed
    to access the audit tools like auditctl, last (wtmpdb) and journalctl. This should
    be applied for the operating system only, but not for containers.
    Ref: SRG-OS-000256-GPOS-00097
    """

    if os.path.exists(AUDIT_LOG_FILE):
        info = os.stat(AUDIT_LOG_FILE)
        assert info.st_uid == 0, f"stigcompliance: {AUDIT_LOG_FILE} not owned by root"

@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_audit_log_not_world_writable():
    """
    As per DISA STIG requirement, we have to ensure that only the root user is allowed
    to access the audit tools like auditctl, last (wtmpdb) and journalctl. This should
    be applied for the operating system only, but not for containers.
    Ref: SRG-OS-000256-GPOS-00097
    """

    if os.path.exists(AUDIT_LOG_FILE):
        info = os.stat(AUDIT_LOG_FILE)
        assert not (
            info.st_mode & stat.S_IWOTH
        ), f"stigcompliance: {AUDIT_LOG_FILE} is world-writable"
