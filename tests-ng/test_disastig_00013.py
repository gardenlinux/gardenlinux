"""
Ref: SRG-OS-000032-GPOS-00013

Verify the operating system monitors remote access methods.
"""

import re

import pytest


@pytest.mark.security_id(203602)
@pytest.mark.booted(reason="requires running sshguard")
@pytest.mark.feature("ssh")
def test_sshguard_is_enabled(systemd):
    """Verify sshguard.service is enabled."""
    assert systemd.is_enabled("sshguard")


@pytest.mark.booted(reason="requires running sshguard")
@pytest.mark.feature("ssh")
@pytest.mark.hypervisor(
    "not qemu", reason="a started sshguard prevents running the testsuite"
)
@pytest.mark.security_id(203602)
def test_sshguard_is_active(systemd):
    """Verify sshguard.service is active."""
    assert systemd.is_active("sshguard")


@pytest.mark.security_id(203602)
@pytest.mark.feature("ssh")
def test_sshguard_journal_reading_is_configured(parse_file):
    """Verify /etc/sshguard/sshguard.conf sets LOGREADER to use journalctl."""
    config = parse_file.parse("/etc/sshguard/sshguard.conf", format="keyval")
    assert "LOGREADER" in config
    assert "journalctl" in config["LOGREADER"]


@pytest.mark.security_id(203602)
@pytest.mark.booted(reason="requires running journald")
@pytest.mark.feature("ssh")
def test_sshguard_can_log_to_journald_dev_log_is_managed_by_journald(file):
    """Verify /dev/log is a symlink to /run/systemd/journal/dev-log."""
    assert file.is_symlink("/dev/log", "/run/systemd/journal/dev-log")


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-rsyslog-default"])
@pytest.mark.feature(
    "disaSTIGmedium",
    reason="auth log routing to /var/log/secure is configured by disaSTIGmedium",
)
@pytest.mark.security_id(203602)
def test_rsyslog_logs_auth_to_secure(parse_file) -> None:
    """Verify rsyslog 50-default.conf routes auth.* to /var/log/secure."""
    assert re.compile(r"auth.*/var/log/secure") in parse_file.lines(
        "/etc/rsyslog.d/50-default.conf"
    )
