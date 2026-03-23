import time

import pytest

IDENTITY_FILES = [
    "/etc/passwd",
    "/etc/shadow",
    "/etc/group",
    "/etc/gshadow",
]

AUDIT_RULE_PATHS = [
    "/etc/audit/rules.d",
    "/etc/audit/audit.rules",
]


@pytest.fixture
def audit_test_user(shell):
    """
    As per DISA STIG compliance requirement, the operating system 
    must audit all account creations.
    Ref: SRG-OS-000004-GPOS-00004
    """
    username = "audit_test_user_stig"

    result_add = shell(f"useradd {username}")
    assert result_add.returncode == 0

    time.sleep(1)

    yield username

    result_del = shell(f"userdel {username}")
    assert result_del.returncode == 0


@pytest.mark.feature(
    "not container and not gardener and not lima and not capi and not baremetal"
)
@pytest.mark.booted(reason="required for audit operations")
@pytest.mark.root(reason="auditctl requires root privileges")
def test_account_creation_audit_rules_loaded(shell):
    """
    As per DISA STIG compliance requirement, the operating system 
    must audit all account creations.
    Ref: SRG-OS-000004-GPOS-00004
    """
    result = shell("auditctl -l")
    assert result.returncode == 0

    stdout = result.stdout or ""

    for path in IDENTITY_FILES:
        assert path in stdout


@pytest.mark.feature(
    "not container and not gardener and not lima and not capi and not baremetal"
)
@pytest.mark.booted(reason="required for audit operations")
@pytest.mark.root(reason="auditctl requires root privileges")
def test_account_creation_audit_rules_config_present(file):
    """
    As per DISA STIG compliance requirement, the operating system 
    must audit all account creations.
    Ref: SRG-OS-000004-GPOS-00004
    """
    assert any(file.exists(path) for path in AUDIT_RULE_PATHS)


@pytest.mark.feature(
    "not container and not gardener and not lima and not capi and not baremetal"
)
@pytest.mark.booted(reason="required for audit operations")
@pytest.mark.root(reason="auditctl requires root privileges")
def test_account_creation_event_logged(shell, audit_test_user):
    """
    As per DISA STIG compliance requirement, the operating system 
    must audit all account creations.
    Ref: SRG-OS-000004-GPOS-00004
    """
    result = shell("ausearch -k identity -ts recent")

    assert result.returncode == 0

    stdout = result.stdout or ""

    assert "/etc/passwd" in stdout or "/etc/shadow" in stdout or "useradd" in stdout
