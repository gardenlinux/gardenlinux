import pytest
from plugins.file import File
from plugins.parse_file import ParseFile

# =============================================================================
# fedramp Feature - Federal Risk and Authorization Management Program
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-fedramp-script-firewall-ipv4-flush",
        "GL-SET-fedramp-script-firewall-ipv6-flush",
        "GL-SET-fedramp-config-firewall-ipv4-gl-default",
        "GL-SET-fedramp-config-firewall-ipv6-gl-default",
    ]
)
@pytest.mark.feature("fedramp")
def test_fedramp_firewall_configs_exist(file: File):
    """Test that FedRAMP firewall configurations exist"""
    configs = [
        "/etc/firewall/ipv4_flush.sh",
        "/etc/firewall/ipv6_flush.sh",
        "/etc/firewall/ipv4_gl_default.conf",
        "/etc/firewall/ipv6_gl_default.conf",
    ]
    missing = [cfg for cfg in configs if not file.exists(cfg)]
    assert not missing, f"Missing FedRAMP firewall configs: {', '.join(missing)}"


@pytest.mark.setting_ids(["GL-SET-fedramp-config-chrony"])
@pytest.mark.feature("fedramp")
def test_fedramp_chrony_config_exists(file: File):
    """Test that FedRAMP chrony configuration exists"""
    assert file.is_regular_file("/etc/chrony/chrony.conf")


@pytest.mark.setting_ids(["GL-SET-fedramp-config-issue-net"])
@pytest.mark.feature("fedramp")
def test_fedramp_issue_net_exists(file: File):
    """Test that FedRAMP issue.net banner exists"""
    assert file.is_regular_file("/etc/issue.net")


@pytest.mark.setting_ids(["GL-SET-fedramp-config-issue-net"])
@pytest.mark.feature("fedramp")
def test_fedramp_issue_net_content(parse_file: ParseFile):
    """Test that FedRAMP issue.net banner content exists"""
    lines = parse_file.lines("/etc/issue.net")
    assert (
        "You are accessing a U.S. Government (USG) Information System (IS) that is provided for USG-authorized use only."
        in lines
    ), "issue.net banner content should contain the correct content"


@pytest.mark.setting_ids(["GL-SET-fedramp-config-security-limits"])
@pytest.mark.feature("fedramp")
def test_fedramp_security_limits_exists(file: File):
    """Test that FedRAMP security limits configuration exists"""
    assert file.is_regular_file("/etc/security/limits.conf")


@pytest.mark.setting_ids(["GL-SET-fedramp-config-security-limits"])
@pytest.mark.feature("fedramp")
def test_fedramp_security_limits_content(parse_file: ParseFile):
    """Test that FedRAMP security limits configuration content exists"""
    lines = parse_file.lines("/etc/security/limits.conf")
    assert (
        "*               -       maxlogins       10" in lines
    ), "security limits configuration should contain the correct content"


@pytest.mark.setting_ids(["GL-SET-fedramp-config-audit-tallylog"])
@pytest.mark.feature("fedramp")
def test_fedramp_audit_tallylog_exists(file: File):
    """Test that FedRAMP audit tallylog configuration exists"""
    assert file.exists("/etc/audit/rules.d/audit.rules")


@pytest.mark.setting_ids(["GL-SET-fedramp-config-audit-tallylog"])
@pytest.mark.feature("fedramp")
def test_fedramp_audit_tallylog_content(parse_file: ParseFile):
    """Test that FedRAMP audit tallylog configuration content exists"""
    lines = parse_file.lines("/etc/audit/rules.d/audit.rules")
    assert (
        "-w /var/log/tallylog -p wa -k logins" in lines
    ), "audit tallylog configuration should contain the correct content"


@pytest.mark.setting_ids(
    [
        "GL-SET-fedramp-config-kernel-cmdline-fips",
        "GL-SET-fedramp-config-kernel-cmdline-lsm",
    ]
)
@pytest.mark.feature("fedramp")
def test_fedramp_kernel_cmdline_configs_exist(file: File):
    """Test that FedRAMP kernel cmdline configs exist"""
    configs = [
        "/etc/kernel/cmdline.d/30-fips.cfg",
        "/etc/kernel/cmdline.d/90-lsm.cfg",
    ]
    missing = [cfg for cfg in configs if not file.is_regular_file(cfg)]
    assert not missing, f"Missing kernel cmdline configs: {', '.join(missing)}"


@pytest.mark.setting_ids(["GL-SET-fedramp-config-kernel-cmdline-fips"])
@pytest.mark.feature("fedramp")
def test_fedramp_kernel_cmdline_fips_content(parse_file: ParseFile):
    """Test that FedRAMP kernel cmdline fips configuration content exists"""
    lines = parse_file.lines("/etc/kernel/cmdline.d/30-fips.cfg")
    assert (
        "fips=1" in lines
    ), "kernel cmdline fips configuration should contain the correct content"


@pytest.mark.setting_ids(["GL-SET-fedramp-config-kernel-cmdline-lsm"])
@pytest.mark.feature("fedramp")
def test_fedramp_kernel_cmdline_lsm_content(parse_file: ParseFile):
    """Test that FedRAMP kernel cmdline lsm configuration content exists"""
    lines = parse_file.lines("/etc/kernel/cmdline.d/90-lsm.cfg")
    assert (
        "security=apparmor" in lines
    ), "kernel cmdline lsm configuration should contain the correct content"


@pytest.mark.setting_ids(["GL-SET-fedramp-config-ssh-sshd-config"])
@pytest.mark.feature("fedramp")
def test_fedramp_sshd_config_exists(file: File):
    """Test that FedRAMP SSHD configuration exists"""
    assert file.is_regular_file("/etc/ssh/sshd_config")


@pytest.mark.setting_ids(["GL-SET-fedramp-config-ssh-sshd-config"])
@pytest.mark.feature("fedramp")
def test_fedramp_sshd_config_content(parse_file: ParseFile):
    """Test that FedRAMP SSHD configuration content exists"""
    lines = parse_file.lines("/etc/ssh/sshd_config")
    assert lines == [
        "PermitRootLogin no",
        "Protocol 2",
        "X11Forwarding no",
        "StrictModes yes",
        "IgnoreRhosts yes",
        "HostbasedAuthentication no",
        "LogLevel VERBOSE",
        "UsePAM yes",
        "PrintMotd no",
        "AcceptEnv LANG",
        "Subsystem sftp /usr/lib/openssh/sftp-server -f AUTHPRIV -l INFO",
        "ClientAliveInterval 600",
        "ClientAliveCountMax 0",
        "AuthenticationMethods publickey",
        "PermitEmptyPasswords no",
        "Banner /etc/issue.net",
        "HostKey /etc/ssh/ssh_host_ed25519_key",
        "HostKey /etc/ssh/ssh_host_rsa_key",
    ]
