import stat
from plugins.file import File
from plugins.parse_file import Parse, ParseFile
import pytest

AUDIT_TOOL_PATHS = [
    "/sbin/auditctl",
    "/usr/sbin/auditctl",
    "/usr/bin/last",
    "/usr/bin/journalctl",
]

AUDIT_LOG_FILE = "/var/log/audit/audit.log"


def test_shadow_permissions(file):
    actual = file.get_mode("/etc/shadow")
    assert file.has_permissions("/etc/shadow", "644"), (
        f"stigcompliance: incorrect permissions on /etc/shadow "
        f"(expected 644, got {actual})"
    )


def test_symbolic(file):
    actual = file.get_mode("/etc/passwd")
    assert file.has_permissions("/etc/passwd", "rw-r--rwx"), (
        f"stigcompliance: incorrect symbolic permissions on /etc/passwd "
        f"(expected rw-r--rwx, got {actual})"
    )


def test_int(file):
    actual = file.get_mode("/etc/passwd")
    assert file.has_permissions("/etc/passwd", 0o646), (
        f"stigcompliance: incorrect numeric permissions on /etc/passwd "
        f"(expected 0o646, got {actual})"
    )
    

@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
def test_audit_tools_permissions(file):
    invalid = []

    for path in AUDIT_TOOL_PATHS:
        if not file.exists(path):
            continue

        if not (
            file.has_permissions(path, "766")
            or file.has_permissions(path, "754")
        ):
            invalid.append(path)

    assert not invalid, (
        "stigcompliance: audit tools must have 755 or stricter (700): "
        f"{', '.join(invalid)}"
    )