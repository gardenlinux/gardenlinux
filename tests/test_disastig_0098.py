import stat
from pathlib import Path

import pytest

AUDIT_LOG_DIR = "/var/log/audit"


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit protection requires booted system")
@pytest.mark.root(reason="required to inspect audit log ownership")
def test_audit_log_directory_protected(file):
    """
    As per DISA STIG it is required to verify the operating system protects audit tools
    from unauthorized modification.
    This test verifies:
      - Audit log directory exists
      - Directory is owned by root
      - Directory is not group/world writable
    Ref: SRG-OS-000257-GPOS-00098
    """

    assert file.exists(AUDIT_LOG_DIR), f"stigcompliance: {AUDIT_LOG_DIR} does not exist"

    assert file.is_owned_by_user(
        AUDIT_LOG_DIR, "root"
    ), f"stigcompliance: {AUDIT_LOG_DIR} must be owned by root"

    mode = int(file.get_mode(AUDIT_LOG_DIR), 8)

    assert not (mode & stat.S_IWGRP or mode & stat.S_IWOTH), (
        f"stigcompliance: {AUDIT_LOG_DIR} is group/world writable "
        f"(mode {file.get_mode(AUDIT_LOG_DIR)})"
    )


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit protection requires booted system")
@pytest.mark.root(reason="required to inspect audit log ownership")
def test_audit_log_files_protected(file):
    """
    As per DISA STIG it is required to verify the operating system protects
    audit log files from unauthorized modification.
    This test verifies:
      - All regular files in /var/log/audit
      - Owned by root
      - Not group/world writable
    Ref: SRG-OS-000257-GPOS-00098
    """

    if not file.exists(AUDIT_LOG_DIR):
        pytest.skip(f"{AUDIT_LOG_DIR} does not exist")

    violations = []

    for path in Path(AUDIT_LOG_DIR).glob("*"):
        if not file.is_regular_file(path):
            continue

        owner_ok = file.is_owned_by_user(path, "root")

        mode = int(file.get_mode(path), 8)
        writable = mode & stat.S_IWGRP or mode & stat.S_IWOTH

        if not owner_ok or writable:
            violations.append(
                f"{path.name} (owner={file.get_user(path)}, mode={file.get_mode(path)})"
            )

    assert (
        not violations
    ), "stigcompliance: audit log files not properly protected for: " + ", ".join(
        violations
    )
