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
def test_audit_tools_owned_by_root(file):
    """
    As per DISA STIG requirement, we have to ensure that only the root user is allowed
    to access the audit tools like auditctl, last (wtmpdb) and journalctl. This should
    be applied for the operating system only, but not for containers.
    Ref: SRG-OS-000256-GPOS-00097
    """

    for path in AUDIT_TOOL_PATHS:
        if file.exists(path):
            assert file.is_owned_by_user(
                path, "root"
            ), f"stigcompliance: {path} not owned by root"


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_audit_tools_not_world_writable(file):
    """
    As per DISA STIG requirement, we have to ensure that only the root user is allowed
    to access the audit tools like auditctl, last (wtmpdb) and journalctl. This should
    be applied for the operating system only, but not for containers.
    Ref: SRG-OS-000256-GPOS-00097
    """

    for path in AUDIT_TOOL_PATHS:
        if file.exists(path):
            mode = file.get_mode(path)
            assert mode[-1] not in {
                "2",
                "3",
                "6",
                "7",
            }, f"stigcompliance: {path} is world-writable (mode {mode})"


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_audit_tools_not_group_writable(file):
    """
    As per DISA STIG requirement, we have to ensure that only the root user is allowed
    to access the audit tools like auditctl, last (wtmpdb) and journalctl. This should
    be applied for the operating system only, but not for containers.
    Ref: SRG-OS-000256-GPOS-00097
    """

    for path in AUDIT_TOOL_PATHS:
        if file.exists(path):
            mode = file.get_mode(path)
            assert mode[-2] not in {
                "2",
                "3",
                "6",
                "7",
            }, f"stigcompliance: {path} is group-writable (mode {mode})"


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_audit_log_owned_by_root(file):
    """
    As per DISA STIG requirement, we have to ensure that only the root user is allowed
    to access the audit tools like auditctl, last (wtmpdb) and journalctl. This should
    be applied for the operating system only, but not for containers.
    Ref: SRG-OS-000256-GPOS-00097
    """

    if file.exists(AUDIT_LOG_FILE):
        assert file.is_owned_by_user(
            AUDIT_LOG_FILE, "root"
        ), f"stigcompliance: {AUDIT_LOG_FILE} not owned by root"


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_audit_log_not_world_writable(file):
    """
    As per DISA STIG requirement, we have to ensure that only the root user is allowed
    to access the audit tools like auditctl, last (wtmpdb) and journalctl. This should
    be applied for the operating system only, but not for containers.
    Ref: SRG-OS-000256-GPOS-00097
    """

    if file.exists(AUDIT_LOG_FILE):
        mode = file.get_mode(AUDIT_LOG_FILE)
        assert mode[-1] not in {
            "2",
            "3",
            "6",
            "7",
        }, f"stigcompliance: {AUDIT_LOG_FILE} is world-writable (mode {mode})"
