"""
Ref: SRG-OS-000362-GPOS-00149

Verify the operating system prohibits user installation of system software
without explicit privileged status.
"""

import pytest
from plugins.file import File

PKG_BINARIES = [
    "/usr/bin/apt",
    "/usr/bin/apt-get",
    "/usr/bin/dpkg",
]


@pytest.mark.feature("not container and not lima")
@pytest.mark.root(reason="required to verify package manager permissions")
@pytest.mark.booted(
    reason="system must be booted to verify package manager permissions"
)
@pytest.mark.security_id(203716)
def test_package_manager_requires_privileged_access(file: File):
    """Verify /usr/bin/apt, apt-get and dpkg are owned by root with mode rwxr-xr-x or stricter."""
    for path in PKG_BINARIES:
        if not file.exists(path):
            continue

        assert file.is_owned_by_user(
            path, "root"
        ), f"stigcompliance: {path} is not owned by root"

        assert (
            file.has_permissions(path, "rwxr-xr-x")
            or file.has_permissions(path, "rwxr-x---")
            or file.has_permissions(path, "rwx------")
        ), f"stigcompliance: {path} permissions are too permissive"


PKG_DB_PATHS = [
    "/var/lib/dpkg",
    "/var/lib/dpkg/status",
]


@pytest.mark.feature("not container and not lima")
@pytest.mark.root(reason="required to verify package database protection")
@pytest.mark.booted(
    reason="system must be booted to verify package database permissions"
)
@pytest.mark.security_id(203716)
def test_package_database_protected(file: File):
    """Verify /var/lib/dpkg and /var/lib/dpkg/status are owned by root with non-world-writable modes."""
    for path in PKG_DB_PATHS:
        if not file.exists(path):
            continue

        assert file.is_owned_by_user(
            path, "root"
        ), f"stigcompliance: {path} is not owned by root"

        assert (
            file.has_permissions(path, "rwxr-xr-x")
            or file.has_permissions(path, "rwxr-x---")
            or file.has_permissions(path, "rwx------")
            or file.has_permissions(path, "rw-r--r--")
            or file.has_permissions(path, "rw-r-----")
            or file.has_permissions(path, "rw-------")
        ), f"stigcompliance: {path} permissions are too permissive"
