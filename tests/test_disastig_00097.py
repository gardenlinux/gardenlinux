import pytest
from plugins.file import Permissions

AUDIT_TOOL_PATHS = [
    "/sbin/auditctl",
    "/usr/sbin/auditctl",
    "/usr/bin/last",
    "/usr/bin/journalctl",
]


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_shadow_permissions(file):
    """
    As per DISA STIG, the operating system must protect audit tools from unauthorized access.
    Ref: SRG-OS-000256-GPOS-00097
    """
    actual = file.get_mode("/etc/shadow")
    testing_file = Permissions("/etc/shadow")

    assert testing_file.has_permissions("0640"), (
        f"stigcompliance: incorrect permissions on /etc/shadow "
        f"(expected 0640, got {actual})"
    )


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_passwd_permissions_numeric(file):
    """
    As per DISA STIG, the operating system must protect audit tools from unauthorized access.
    Ref: SRG-OS-000256-GPOS-00097
    """
    actual = file.get_mode("/etc/passwd")
    testing_file = Permissions("/etc/passwd")

    assert testing_file.has_permissions("0644"), (
        f"stigcompliance: incorrect permissions on /etc/passwd "
        f"(expected 0644, got {actual})"
    )


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_passwd_permissions_symbolic(file):
    """
    As per DISA STIG, the operating system must protect audit tools from unauthorized access.
    Ref: SRG-OS-000256-GPOS-00097
    """
    actual = file.get_mode("/etc/passwd")
    testing_file = Permissions("/etc/passwd")

    assert testing_file.has_permissions("rw-r--r--"), (
        f"stigcompliance: incorrect symbolic permissions on /etc/passwd "
        f"(expected rw-r--r--, got {actual})"
    )


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="audit tools check requires booted system")
@pytest.mark.root(reason="required to execute privileged tools")
def test_audit_tools_permissions(file):
    """
    As per DISA STIG, the operating system must protect audit tools from unauthorized access.
    Ref: SRG-OS-000256-GPOS-00097
    """
    invalid = []

    for path in AUDIT_TOOL_PATHS:
        if not file.exists(path):
            continue

        testing_file = Permissions(path)

        if not testing_file.has_permissions("755"):
            invalid.append(f"{path} ({file.get_mode(path)})")

    assert not invalid, (
        "stigcompliance: audit tools must have 755: " f"{', '.join(invalid)}"
    )
