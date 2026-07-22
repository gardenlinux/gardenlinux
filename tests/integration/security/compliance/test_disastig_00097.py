"""
Ref: SRG-OS-000256-GPOS-00097

Verify the operating system protects audit tools from unauthorized access.
"""

import pytest

AUDIT_TOOL_PATHS = [
    "/sbin/auditctl",
    "/usr/sbin/auditctl",
    "/usr/bin/last",
    "/usr/bin/journalctl",
]


@pytest.mark.security_id(203672)
@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_shadow_permissions(file):
    """Verify /etc/shadow has mode 0640."""
    actual = file.get_mode("/etc/shadow")
    assert file.has_permissions("/etc/shadow", "0640"), (
        f"stigcompliance: incorrect permissions on /etc/shadow "
        f"(expected 640, got {actual})"
    )


@pytest.mark.security_id(203672)
@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_passwd_permissions_numeric(file):
    """Verify /etc/passwd has numeric mode 0644."""
    actual = file.get_mode("/etc/passwd")
    assert file.has_permissions("/etc/passwd", "0644"), (
        f"stigcompliance: incorrect permissions on /etc/passwd "
        f"(expected 0644, got {actual})"
    )


@pytest.mark.security_id(203672)
@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_passwd_permissions_symbolic(file):
    """Verify /etc/passwd has symbolic mode rw-r--r--."""
    actual = file.get_mode("/etc/passwd")
    assert file.has_permissions("/etc/passwd", "rw-r--r--"), (
        f"stigcompliance: incorrect symbolic permissions on /etc/passwd "
        f"(expected rw-r--r--, got {actual})"
    )


@pytest.mark.security_id(203672)
@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
def test_audit_tools_permissions(file):
    """Verify auditctl, last and journalctl binaries have mode 755."""
    invalid = []

    for path in AUDIT_TOOL_PATHS:
        if not file.exists(path):
            continue

        if not file.has_permissions(path, "755"):
            invalid.append(f"{path} ({file.get_mode(path)})")

    assert not invalid, (
        "stigcompliance: audit tools must have 755: " f"{', '.join(invalid)}"
    )


@pytest.mark.security_id(203672)
@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_sticky_bit_support(file, tmp_path):
    """Verify a tmp directory chmod-ed to 1777 reports both 1777 and rwxrwxrwt."""
    test_dir = tmp_path / "sticky_test"
    test_dir.mkdir()
    test_dir.chmod(0o1777)

    assert file.has_permissions(test_dir, "1777")
    assert file.has_permissions(test_dir, "rwxrwxrwt")
