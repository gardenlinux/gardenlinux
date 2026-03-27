import pytest

"""
Ref: SRG-OS-000032-GPOS-00013

Verify the operating system monitors remote access methods.
"""


@pytest.mark.booted(reason="requires running sshguard")
@pytest.mark.feature("ssh")
def test_sshguard_is_enabled(systemd):
    """
    sshguard blocks and logs IP addresses that brute-force ssh access
    """
    assert systemd.is_active("sshguard")


@pytest.mark.feature("ssh")
def test_sshguard_journal_reading_is_configured(parse_file):
    """
    sshguard by itself reads ssh logs to know about access attempts
    """
    config = parse_file.parse("/etc/sshguard/sshguard.conf", format="keyval")
    assert "LOGREADER" in config
    assert "journalctl" in config["LOGREADER"]


@pytest.mark.booted(reason="requires running journald")
@pytest.mark.feature("ssh")
def test_sshguard_can_log_to_journald_dev_log_is_managed_by_journald(file):
    """
    sshguard logs IPs that it blocked:
    https://github.com/riptideio/sshguard/blob/3ecd86cee72ba672f728653f5f56df4126584356/src/blocker/blocker.c#L164
    to syslog:
    https://github.com/riptideio/sshguard/blob/3ecd86cee72ba672f728653f5f56df4126584356/src/blocker/sshguard_log.h#L26
    but since journald owns /dev/log it can "intercept" those messages
    """
    assert file.is_symlink("/dev/log", "/run/systemd/journal/dev-log")
