import os
import stat

import pytest


def _is_container() -> bool:
    return os.path.exists("/.dockerenv") or os.path.exists("/run/.containerenv")


@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_auditctl_owned_by_root():
    """
    As per DISA STIG requirement, we have to ensure that only the root user is allowed
    to access the audit tools like auditctl, last (wtmpdb) and journalctl. This should
    be applied for the operating system only, but not for containers.
    Ref: SRG-OS-000256-GPOS-00097
    """

    if _is_container():
        pytest.skip(
            "stigcompliance: skipping containers for audit control requirements"
        )

    paths = [
        "/sbin/auditctl",
        "/usr/sbin/auditctl",
        "/usr/bin/last",
        "/usr/bin/journalctl",
    ]

    for path in paths:
        if os.path.exists(path):
            info = os.stat(path)
            assert info.st_uid == 0, f"stigcompliance: {path} not owned by root"


@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_auditctl_not_world_writable():
    """
    As per DISA STIG requirement, we have to ensure that only the root user is allowed
    to access the audit tools like auditctl, last (wtmpdb) and journalctl. This should
    be applied for the operating system only, but not for containers.
    Ref: SRG-OS-000256-GPOS-00097
    """

    if _is_container():
        pytest.skip(
            "stigcompliance: skipping containers for audit control requirements"
        )

    paths = [
        "/sbin/auditctl",
        "/usr/sbin/auditctl",
        "/usr/bin/last",
        "/usr/bin/journalctl",
    ]

    for path in paths:
        if os.path.exists(path):
            info = os.stat(path)
            assert not (
                info.st_mode & stat.S_IWOTH
            ), f"stigcompliance: {path} is world-writable"


@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_auditctl_not_group_writable():
    """
    As per DISA STIG requirement, we have to ensure that only the root user is allowed
    to access the audit tools like auditctl, last (wtmpdb) and journalctl. This should
    be applied for the operating system only, but not for containers.
    Ref: SRG-OS-000256-GPOS-00097
    """

    if _is_container():
        pytest.skip(
            "stigcompliance: skipping containers for audit control requirements"
        )

    paths = [
        "/sbin/auditctl",
        "/usr/sbin/auditctl",
        "/usr/bin/last",
        "/usr/bin/journalctl",
    ]

    for path in paths:
        if os.path.exists(path):
            info = os.stat(path)
            assert not (
                info.st_mode & stat.S_IWGRP
            ), f"stigcompliance: {path} is group-writable"


@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_audit_log_owned_by_root():
    """
    As per DISA STIG requirement, we have to ensure that only the root user is allowed
    to access the audit tools like auditctl, last (wtmpdb) and journalctl. This should
    be applied for the operating system only, but not for containers.
    Ref: SRG-OS-000256-GPOS-00097
    """

    if _is_container():
        pytest.skip(
            "stigcompliance: skipping containers for audit control requirements"
        )

    log_file = "/var/log/audit/audit.log"

    if os.path.exists(log_file):
        info = os.stat(log_file)
        assert info.st_uid == 0, f"stigcompliance: {log_file} not owned by root"


@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_audit_log_not_world_writable():
    """
    As per DISA STIG requirement, we have to ensure that only the root user is allowed
    to access the audit tools like auditctl, last (wtmpdb) and journalctl. This should
    be applied for the operating system only, but not for containers.
    Ref: SRG-OS-000256-GPOS-00097
    """

    if _is_container():
        pytest.skip(
            "stigcompliance: skipping containers for audit control requirements"
        )

    log_file = "/var/log/audit/audit.log"

    if os.path.exists(log_file):
        info = os.stat(log_file)
        assert not (
            info.st_mode & stat.S_IWOTH
        ), f"stigcompliance: {log_file} is world-writable"
