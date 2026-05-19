import pytest

"""
Coverage tests for disaSTIGmedium OS-level configuration markers that are not
covered by dedicated per-rule test files.

Refs:
    SRG-OS-000373-GPOS-00156  (sudoers wheel)
    SRG-OS-000480-GPOS-00228  (login.defs UMASK)
    SRG-OS-000205-GPOS-00083  (var/log permissions)
    SRG-OS-000109-GPOS-00056  (root locked)
    SRG-OS-000120-GPOS-00061  (login.defs ENCRYPT_METHOD)
    SRG-OS-000118-GPOS-00060  (useradd INACTIVE)
    SRG-OS-000279-GPOS-00109  (terminal TMOUT)
    SRG-OS-000142-GPOS-00071  (sysctl disaSTIG conf)
    SRG-OS-000032-GPOS-00013  (rsyslog auth logging)
"""

SUDOERS_WHEEL = "/etc/sudoers.d/wheel"
LOGIN_DEFS = "/etc/login.defs"
VAR_LOG = "/var/log"
USERADD_DEFAULTS = "/etc/default/useradd"
TMOUT_PROFILE = "/etc/profile.d/99-terminal_tmout.sh"
SYSCTL_DISASTIG = "/etc/sysctl.d/99-disaSTIG.conf"
RSYSLOG_DEFAULT = "/etc/rsyslog.d/50-default.conf"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-sudoers-wheel"])
@pytest.mark.feature("disaSTIGmedium")
def test_sudoers_wheel_file_exists(file):
    """Verify /etc/sudoers.d/wheel exists (created/truncated by disaSTIGmedium)."""
    assert file.exists(SUDOERS_WHEEL), f"stigcompliance: {SUDOERS_WHEEL} does not exist"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-sudoers-wheel"])
@pytest.mark.feature("disaSTIGmedium")
def test_sudoers_wheel_file_is_empty(file):
    """Verify /etc/sudoers.d/wheel is empty (disaSTIGmedium truncates it with echo -n)."""
    assert (
        file.get_size(SUDOERS_WHEEL) == 0
    ), f"stigcompliance: {SUDOERS_WHEEL} is not empty (size={file.get_size(SUDOERS_WHEEL)})"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-login-defs-umask"])
@pytest.mark.feature("disaSTIGmedium")
def test_login_defs_umask_is_077(parse_file):
    """Verify UMASK in /etc/login.defs is set to 077 (SRG-OS-000480-GPOS-00228)."""
    config = parse_file.parse(LOGIN_DEFS, format="spacedelim")
    assert (
        config["UMASK"] == "077"
    ), f"stigcompliance: UMASK in {LOGIN_DEFS} is {config['UMASK']!r}, expected '077'"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-var-log-file-permissions"])
@pytest.mark.feature("disaSTIGmedium")
def test_var_log_has_755_permissions(file):
    """Verify /var/log directory has permissions 755 (SRG-OS-000205-GPOS-00083)."""
    assert file.has_permissions(
        VAR_LOG, "rwxr-xr-x"
    ), f"stigcompliance: {VAR_LOG} permissions are {file.get_mode(VAR_LOG)!r}, expected 0755"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-root-locked"])
@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.root(reason="requires root to read shadow password status")
def test_root_account_is_locked(shell):
    """Verify root account is locked (field 2 of passwd --status output is 'L')."""
    result = shell("passwd --status root", capture_output=True, ignore_exit_code=True)
    fields = result.stdout.split()
    assert (
        len(fields) >= 2 and fields[1] == "L"
    ), f"stigcompliance: root account is not locked (passwd --status output: {result.stdout!r})"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-login-defs-encrypt"])
@pytest.mark.feature("disaSTIGmedium")
def test_login_defs_encrypt_method_is_sha512(parse_file):
    """Verify ENCRYPT_METHOD in /etc/login.defs is SHA512 (SRG-OS-000120-GPOS-00061)."""
    config = parse_file.parse(LOGIN_DEFS, format="spacedelim")
    assert config["ENCRYPT_METHOD"] == "SHA512", (
        f"stigcompliance: ENCRYPT_METHOD in {LOGIN_DEFS} is "
        f"{config['ENCRYPT_METHOD']!r}, expected 'SHA512'"
    )


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-useradd-inactive"])
@pytest.mark.feature("disaSTIGmedium")
def test_useradd_inactive_is_35(parse_file):
    """Verify INACTIVE in /etc/default/useradd is 35 (SRG-OS-000118-GPOS-00060)."""
    config = parse_file.parse(USERADD_DEFAULTS, format="keyval")
    assert (
        config["INACTIVE"] == "35"
    ), f"stigcompliance: INACTIVE in {USERADD_DEFAULTS} is {config['INACTIVE']!r}, expected '35'"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-profile-terminal-tmout"])
@pytest.mark.feature("disaSTIGmedium")
def test_terminal_tmout_profile_sets_tmout_900(parse_file):
    """Verify /etc/profile.d/99-terminal_tmout.sh contains TMOUT=900 (SRG-OS-000279-GPOS-00109)."""
    lines = parse_file.lines(TMOUT_PROFILE)
    assert any(
        "TMOUT=900" in line for line in lines
    ), f"stigcompliance: {TMOUT_PROFILE} does not contain 'TMOUT=900'"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-sysctl-disaSTIG"])
@pytest.mark.feature("disaSTIGmedium")
def test_sysctl_disastig_conf_exists(file):
    """Verify /etc/sysctl.d/99-disaSTIG.conf exists (SRG-OS-000142-GPOS-00071)."""
    assert file.exists(
        SYSCTL_DISASTIG
    ), f"stigcompliance: {SYSCTL_DISASTIG} does not exist"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-rsyslog-default"])
@pytest.mark.feature("disaSTIGmedium")
def test_rsyslog_logs_auth_to_secure(parse_file):
    """Verify auth/authpriv logging to /var/log/secure in rsyslog (SRG-OS-000032-GPOS-00013)."""
    lines = parse_file.lines(RSYSLOG_DEFAULT)
    assert any(
        "auth" in line and "/var/log/secure" in line for line in lines
    ), f"stigcompliance: {RSYSLOG_DEFAULT} does not route auth logs to /var/log/secure"


# =============================================================================
# disaSTIGlow markers
# Refs:
#   SRG-OS-000343-GPOS-00134  (auditd.conf)
#   SRG-OS-000329-GPOS-00128  (faillock)
#   SRG-OS-000027-GPOS-00008  (limits)
#   SRG-OS-000070-GPOS-00038  (pwquality)
#   SRG-OS-000138-GPOS-00069  (sysctl disaSTIGlow)
# =============================================================================

AUDITD_CONF = "/etc/audit/auditd.conf"
FAILLOCK_CONF = "/etc/security/faillock.conf"
LIMITS_CONF = "/etc/security/limits.conf"
PWQUALITY_CONF = "/etc/security/pwquality.conf"
SYSCTL_DISASTIG_LOW = "/etc/sysctl.d/99-disaSTIG.conf"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGlow-config-audit-auditd-conf"])
@pytest.mark.feature("disaSTIGlow")
def test_auditd_conf_disk_full_action_is_halt(parse_file):
    """Verify disk_full_action=halt in auditd.conf (SRG-OS-000343-GPOS-00134)."""
    config = parse_file.parse(AUDITD_CONF, format="keyval")
    assert config["disk_full_action"] == "halt", (
        f"stigcompliance: disk_full_action in {AUDITD_CONF} is "
        f"{config['disk_full_action']!r}, expected 'halt'"
    )


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGlow-config-security-faillock"])
@pytest.mark.feature("disaSTIGlow")
def test_faillock_deny_is_3(parse_file):
    """Verify deny=3 in faillock.conf (SRG-OS-000329-GPOS-00128)."""
    config = parse_file.parse(FAILLOCK_CONF, format="keyval")
    assert (
        config["deny"] == "3"
    ), f"stigcompliance: deny in {FAILLOCK_CONF} is {config['deny']!r}, expected '3'"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGlow-config-security-limits"])
@pytest.mark.feature("disaSTIGlow")
def test_limits_conf_maxlogins_is_10(parse_file):
    """Verify hard maxlogins 10 in limits.conf (SRG-OS-000027-GPOS-00008)."""
    lines = parse_file.lines(LIMITS_CONF)
    assert any(
        "hard" in line and "maxlogins" in line and "10" in line for line in lines
    ), f"stigcompliance: {LIMITS_CONF} does not contain 'hard maxlogins 10'"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGlow-config-security-pwquality"])
@pytest.mark.feature("disaSTIGlow")
def test_pwquality_conf_lcredit_is_minus_1(parse_file):
    """Verify lcredit=-1 in pwquality.conf (SRG-OS-000070-GPOS-00038)."""
    config = parse_file.parse(PWQUALITY_CONF, format="keyval")
    assert (
        config["lcredit"] == "-1"
    ), f"stigcompliance: lcredit in {PWQUALITY_CONF} is {config['lcredit']!r}, expected '-1'"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGlow-config-sysctl-disaSTIG"])
@pytest.mark.feature("disaSTIGlow")
def test_sysctl_disastig_low_conf_exists(file):
    """Verify /etc/sysctl.d/99-disaSTIG.conf exists for disaSTIGlow (SRG-OS-000138-GPOS-00069)."""
    assert file.exists(
        SYSCTL_DISASTIG_LOW
    ), f"stigcompliance: {SYSCTL_DISASTIG_LOW} does not exist"
