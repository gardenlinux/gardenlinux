from unittest.mock import MagicMock, patch

from plugins.audit import AuditRule


def create_mock_audit_rule(rules_text):
    """
    Helper to instantiate AuditRule by mocking the system dependencies
    (Dpkg and subprocess.run) to return the provided rules_text.
    """
    with patch("plugins.audit.Dpkg") as mock_dpkg, patch(
        "plugins.audit.subprocess.run"
    ) as mock_run:
        mock_dpkg.return_value.package_is_installed.return_value = True
        mock_run.return_value = MagicMock(stdout=rules_text, returncode=0)
        return AuditRule()


def test_file_path_audit_rule():
    # Test watch rules (-w)
    rules = "-w /etc/passwd -p wa -k passwd_changes"
    audit = create_mock_audit_rule(rules)

    assert audit.file_path_audit_rule("/etc/passwd", "wa") is True
    assert audit.file_path_audit_rule("/etc/passwd", "r") is False
    assert audit.file_path_audit_rule("/etc/passwd/foo", "wa") is True
    assert audit.file_path_audit_rule("/tmp/foo", "wa") is False


def test_syscall_audit_rule():
    # Test syscall rules (-S) with filters (-F)
    rules = "-a always,exit -S setcap -F auid>=1000 -k setcap_limit"
    audit = create_mock_audit_rule(rules)

    assert audit.syscall_audit_rule("setcap", ["auid>=1000"]) is True
    assert audit.syscall_audit_rule("setcap", ["auid<1000"]) is False
    assert audit.syscall_audit_rule("open", ["auid>=1000"]) is False


def test_binary_call_audit_rule():
    # Test binary execution rules (execve + exe=)
    rules = (
        "-a always,exit -S execve -F exe=/usr/bin/passwd -F auid>=1000 -k passwd_exec"
    )
    audit = create_mock_audit_rule(rules)

    assert audit.binary_call_audit_rule("/usr/bin/passwd", ["auid>=1000"]) is True
    assert audit.binary_call_audit_rule("/usr/bin/passwd", ["auid<1000"]) is False
    assert audit.binary_call_audit_rule("/usr/bin/sudo", ["auid>=1000"]) is False


def test_audit_rule_call():
    # Test the __call__ dispatcher
    rules = """
    -w /etc/passwd -p wa -k passwd_changes
    -a always,exit -S setcap -F auid>=1000 -k setcap_limit
    -a always,exit -S execve -F exe=/usr/bin/passwd -F auid>=1000 -k passwd_exec
    """
    audit = create_mock_audit_rule(rules)

    assert audit(fs_watch_path="/etc/passwd", access_types="wa") is True
    assert audit(syscall="setcap", rule_fields=["auid>=1000"]) is True
    assert audit(binary_call="/usr/bin/passwd", rule_fields=["auid>=1000"]) is True
    assert audit(syscall="open") is False
