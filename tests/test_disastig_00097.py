import stat

import pytest

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

    not_root_owned = [
        path
        for path in AUDIT_TOOL_PATHS
        if file.exists(path) and not file.is_owned_by_user(path, "root")
    ]

    assert not not_root_owned, (
        "stigcompliance: tools not owned by root: " f"{', '.join(not_root_owned)}"
    )


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_audit_tools_not_group_or_world_writable(file):
    """
    As per DISA STIG requirement, we have to ensure that only the root user is allowed
    to access the audit tools like auditctl, last (wtmpdb) and journalctl. This should
    be applied for the operating system only, but not for containers.
    Ref: SRG-OS-000256-GPOS-00097
    """

    writable_tools = []

    for path in AUDIT_TOOL_PATHS:
        if file.exists(path):
            mode = int(file.get_mode(path), 8)
            if mode & stat.S_IWGRP or mode & stat.S_IWOTH:
                writable_tools.append(f"{path} ({file.get_mode(path)})")

    assert not writable_tools, (
        "stigcompliance: tools writable by group/world: " f"{', '.join(writable_tools)}"
    )


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
        ), f"stigcompliance: {AUDIT_LOG_FILE} must be owned by root"


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_audit_log_not_group_or_world_writable(file):
    """
    As per DISA STIG requirement, we have to ensure that only the root user is allowed
    to access the audit tools like auditctl, last (wtmpdb) and journalctl. This should
    be applied for the operating system only, but not for containers.
    Ref: SRG-OS-000256-GPOS-00097
    """

    if file.exists(AUDIT_LOG_FILE):
        mode = int(file.get_mode(AUDIT_LOG_FILE), 8)

        assert not (mode & stat.S_IWGRP or mode & stat.S_IWOTH), (
            f"stigcompliance: {AUDIT_LOG_FILE} writable by group/world "
            f"(mode {file.get_mode(AUDIT_LOG_FILE)})"
        )
