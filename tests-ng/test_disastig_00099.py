"""
Ref: SRG-OS-000258-GPOS-00099

Verify the operating system protects audit tools from unauthorized deletion.
"""

from pathlib import Path

import pytest

AUDIT_TOOL_PATHS = [
    "/sbin/auditctl",
    "/usr/sbin/auditctl",
    "/usr/bin/last",
    "/usr/bin/journalctl",
]


@pytest.mark.security_id(203674)
@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_audit_tools_parent_dirs_not_writable(file):
    """Verify the parent directories of auditctl/last/journalctl are not rwxrwxrwx, rwxrwxr-x or rwxrwx---."""
    checked = set()
    for path in AUDIT_TOOL_PATHS:
        if not file.exists(path):
            continue

        parent = str(Path(path).parent)
        if parent in checked:
            continue
        checked.add(parent)

        mode = file.get_mode(parent)

        assert (
            not file.has_permissions(parent, "rwxrwxrwx")
            and not file.has_permissions(parent, "rwxrwxr-x")
            and not file.has_permissions(parent, "rwxrwx---")
        ), (
            f"stigcompliance: parent directory {parent} allows unauthorized deletion "
            f"(mode: {mode})"
        )
