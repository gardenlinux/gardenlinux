import pytest

AUDIT_TOOL_PATHS = [
    "/sbin/auditctl",
    "/usr/sbin/auditctl",
    "/usr/bin/last",
    "/usr/bin/journalctl",
]


def test_shadow_permissions(file):
    actual = file.get_mode("/etc/shadow")
    assert file.has_permissions("/etc/shadow", "0640"), (
        f"stigcompliance: incorrect permissions on /etc/shadow "
        f"(expected 640, got {actual})"
    )


def test_passwd_permissions_numeric(file):
    actual = file.get_mode("/etc/passwd")
    assert file.has_permissions("/etc/passwd", "0644"), (
        f"stigcompliance: incorrect permissions on /etc/passwd "
        f"(expected 0644, got {actual})"
    )


def test_passwd_permissions_symbolic(file):
    actual = file.get_mode("/etc/passwd")
    assert file.has_permissions("/etc/passwd", "rw-r--r--"), (
        f"stigcompliance: incorrect symbolic permissions on /etc/passwd "
        f"(expected rw-r--r--, got {actual})"
    )


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
def test_audit_tools_permissions(file):
    invalid = []

    for path in AUDIT_TOOL_PATHS:
        if not file.exists(path):
            continue

        if not file.has_permissions(path, "755"):
            invalid.append(f"{path} ({file.get_mode(path)})")

    assert not invalid, (
        "stigcompliance: audit tools must have 755: "
        f"{', '.join(invalid)}"
    )


def test_sticky_bit_support(file, tmp_path):
    """Validate sticky bit handling using temporary directory."""
    test_dir = tmp_path / "sticky_test"
    test_dir.mkdir()
    test_dir.chmod(0o1777)

    assert file.has_permissions(test_dir, "1777")
    assert file.has_permissions(test_dir, "rwxrwxrwt")