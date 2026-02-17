from typing import List

import pytest
from plugins.file import File
from plugins.linux_etc_files import Shadow
from plugins.pam import PamConfig
from plugins.parse_file import ParseFile


@pytest.mark.setting_ids(
    [
        "GL-SET-cis-config-cis-hardening",
    ]
)
@pytest.mark.feature("cis")
@pytest.mark.root(reason="CIS audit requires root privileges")
@pytest.mark.booted(reason="Must be run on a booted system")
@pytest.mark.modify(reason="CIS audit script marked for modifying")
def test_debian_cis_audit(shell):
    """
    Run the Debian CIS audit script and fail if any check shows 'KO'.
    """
    result = shell(
        "/opt/cis-hardening/bin/hardening.sh --audit --allow-unsupported-distribution",
        capture_output=True,
        ignore_exit_code=True,
    )

    output = result.stdout + result.stderr

    # Correct condition grouping:
    #   - Match lines with KO
    #   - Exclude any line containing "Check Failed"
    failed_lines = [
        line.strip()
        for line in output.splitlines()
        if ("Check Failed" not in line)
        and (" KO " in line or line.strip().endswith("KO"))
    ]

    # Remove duplicate lines (same test printed twice)
    unique_failed = sorted(set(failed_lines))

    if unique_failed:
        summary = "\n".join(f"FAILED {line}" for line in unique_failed)
        raise AssertionError(f"{len(unique_failed)} CIS check(s) failed:\n{summary}")

    # Ensure CIS script itself didn't fail
    assert "Check Failed" not in output, "CIS audit run itself failed unexpectedly"


# =============================================================================
# cisAudit Feature - Audit Configuration
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-cisAudit-config-audit-cis"])
@pytest.mark.feature("cisAudit")
def test_cisaudit_audit_rules_exist(file: File):
    """Test that CIS audit rules file exists"""
    assert file.is_regular_file("/etc/audit/rules.d/99-cis.rules")


@pytest.mark.setting_ids(["GL-SET-cisAudit-config-service-audit-rules-override"])
@pytest.mark.feature("cisAudit")
def test_cisaudit_audit_rules_service_override_exists(file: File):
    """Test that audit-rules service override exists"""
    assert file.is_regular_file(
        "/etc/systemd/system/audit-rules.service.d/override.conf"
    )


@pytest.mark.setting_ids(
    [
        "GL-SET-cisAudit-config-audit-space-left-action",
        "GL-SET-cisAudit-config-audit-admin-space-left-action",
        "GL-SET-cisAudit-config-audit-max-log-file-action",
    ]
)
@pytest.mark.feature("cisAudit")
def test_cisaudit_auditd_conf_settings(file: File):
    """Test that auditd.conf has correct CIS settings"""
    auditd_conf = "/etc/audit/auditd.conf"
    assert file.is_regular_file(auditd_conf)

    content = open(auditd_conf).read()

    # Check space_left_action = email
    assert (
        "space_left_action = email" in content
    ), "auditd.conf should have 'space_left_action = email'"

    # Check admin_space_left_action = halt
    assert (
        "admin_space_left_action = halt" in content
    ), "auditd.conf should have 'admin_space_left_action = halt'"

    # Check max_log_file_action = keep_logs
    assert (
        "max_log_file_action = keep_logs" in content
    ), "auditd.conf should have 'max_log_file_action = keep_logs'"


# =============================================================================
# cisOS Feature - Kernel Configuration
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-cisOS-config-kernel-cmdline-audit-proc"])
@pytest.mark.feature("cisOS")
def test_cisos_kernel_cmdline_audit_proc_exists(file: File):
    """Test that audit=1 kernel cmdline config exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/10-audit-proc.cfg")


@pytest.mark.setting_ids(["GL-SET-cisOS-config-kernel-cmdline-audit-backlog"])
@pytest.mark.feature("cisOS")
def test_cisos_kernel_cmdline_audit_backlog_exists(file: File):
    """Test that audit_backlog_limit kernel cmdline config exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/20-audit-backlog.cfg")


# test for audit=1 kernel cmdline config
@pytest.mark.setting_ids(
    [
        "GL-SET-cisOS-config-kernel-cmdline-audit-proc",
        "GL-SET-cisOS-config-kernel-cmdline-audit-backlog",
    ]
)
@pytest.mark.feature("cisOS")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_cisos_kernel_cmdline_audit_runtime(kernel_cmdline: List[str]):
    """Test kernel command line parameters are present in the running kernel command line for CIS OS"""
    required_params = ["audit=1", "audit_backlog_limit=8192"]
    missing = [param for param in required_params if param not in kernel_cmdline]
    assert (
        not missing
    ), f"The following kernel cmdline parameters were not found: {', '.join(missing)}"


@pytest.mark.setting_ids(
    [
        "GL-SET-cisOS-config-kernel-postinst-kernel-cmdline",
        "GL-SET-cisOS-config-kernel-postinst-kernel-install",
        "GL-SET-cisOS-config-kernel-postinst-update-syslinux",
    ]
)
@pytest.mark.feature("cisOS")
def test_cisos_kernel_postinst_hooks_exist(file: File):
    """Test that kernel postinst hooks exist"""
    hooks = [
        "/etc/kernel/postinst.d/zz-kernel-cmdline",
        "/etc/kernel/postinst.d/zz-kernel-install",
        "/etc/kernel/postinst.d/zz-update-syslinux",
    ]
    missing = [hook for hook in hooks if not file.exists(hook)]
    assert not missing, f"Missing kernel postinst hooks: {', '.join(missing)}"


@pytest.mark.setting_ids(
    [
        "GL-SET-cisOS-config-kernel-postrm-kernel-remove",
        "GL-SET-cisOS-config-kernel-postrm-update-syslinux",
    ]
)
@pytest.mark.feature("cisOS")
def test_cisos_kernel_postrm_hooks_exist(file: File):
    """Test that kernel postrm hooks exist"""
    hooks = [
        "/etc/kernel/postrm.d/zz-kernel-remove",
        "/etc/kernel/postrm.d/zz-update-syslinux",
    ]
    missing = [hook for hook in hooks if not file.exists(hook)]
    assert not missing, f"Missing kernel postrm hooks: {', '.join(missing)}"


# =============================================================================
# cisOS Feature - Log Rotation
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-cisOS-config-logrotate-btmp",
        "GL-SET-cisOS-config-logrotate-wtmp",
    ]
)
@pytest.mark.feature("cisOS")
def test_cisos_logrotate_configs_exist(file: File):
    """Test that logrotate configs for btmp and wtmp exist"""
    configs = [
        "/etc/logrotate.d/btmp",
        "/etc/logrotate.d/wtmp",
    ]
    missing = [cfg for cfg in configs if not file.exists(cfg)]
    assert not missing, f"Missing logrotate configs: {', '.join(missing)}"


# =============================================================================
# cisOS Feature - PAM Configuration
# =============================================================================


@pytest.mark.parametrize(
    "pam_config", ["/etc/pam.d/common-account"], indirect=["pam_config"]
)
@pytest.mark.setting_ids(["GL-SET-cisOS-config-pam-common-account"])
@pytest.mark.feature("cisOS")
def test_cisos_pam_common_account_config(pam_config: PamConfig):
    """Test that PAM common-account has correct CIS entries"""
    # Check for pam_faillock.so at the top
    faillock_entries = pam_config.find_entries(
        type_="account", control_contains="required", module_contains="pam_faillock.so"
    )
    assert (
        len(faillock_entries) > 0
    ), "pam_faillock.so should be configured in account stack"

    # Check for pam_unix.so in account stack
    unix_entries = pam_config.find_entries(
        type_="account", module_contains="pam_unix.so"
    )
    assert len(unix_entries) > 0, "pam_unix.so should be configured in account stack"

    # Check for pam_permit.so in account stack
    permit_entries = pam_config.find_entries(
        type_="account", control_contains="required", module_contains="pam_permit.so"
    )
    assert (
        len(permit_entries) > 0
    ), "pam_permit.so should be configured in account stack"


@pytest.mark.parametrize(
    "pam_config", ["/etc/pam.d/common-auth"], indirect=["pam_config"]
)
@pytest.mark.setting_ids(["GL-SET-cisOS-config-pam-common-auth"])
@pytest.mark.feature("cisOS")
def test_cisos_pam_common_auth_config(pam_config: PamConfig):
    """Test that PAM common-auth has correct CIS entries"""
    # Check for pam_faillock.so at the top with correct args
    faillock_entries = pam_config.find_entries(
        type_="auth",
        control_contains="required",
        module_contains="pam_faillock.so",
        arg_contains=["deny=5", "unlock_time=900"],
    )
    assert (
        len(faillock_entries) > 0
    ), "pam_faillock.so should be configured with correct args in auth stack"

    # Check for pam_unix.so in auth stack with nullok
    unix_entries = pam_config.find_entries(
        type_="auth", module_contains="pam_unix.so", arg_contains=["nullok"]
    )
    assert (
        len(unix_entries) > 0
    ), "pam_unix.so should be configured with nullok in auth stack"

    # Check for pam_permit.so in auth stack
    permit_entries = pam_config.find_entries(
        type_="auth", control_contains="required", module_contains="pam_permit.so"
    )
    assert len(permit_entries) > 0, "pam_permit.so should be configured in auth stack"

    # Check for pam_deny.so in auth stack
    deny_entries = pam_config.find_entries(
        type_="auth", control_contains="requisite", module_contains="pam_deny.so"
    )
    assert len(deny_entries) > 0, "pam_deny.so should be configured in auth stack"


# =============================================================================
# cisOS Feature - Security Configuration
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-cisOS-config-security-limits-conf"])
@pytest.mark.feature("cisOS")
def test_cisos_security_limits_conf_exists(file: File):
    """Test that security limits.conf exists"""
    assert file.is_regular_file("/etc/security/limits.conf")


@pytest.mark.setting_ids(["GL-SET-cisOS-config-security-limits-conf"])
@pytest.mark.feature("cisOS")
def test_cisos_security_limits_conf_content(parse_file: ParseFile):
    """Test that security limits.conf has correct content"""
    lines = parse_file.lines("/etc/security/limits.conf")
    assert "* hard core 0" in lines, "hard core should be 0"
    assert "* soft core 0" in lines, "soft core should be 0"


@pytest.mark.setting_ids(["GL-SET-cisOS-config-selinux-config"])
@pytest.mark.feature("cisOS")
def test_cisos_selinux_config_exists(file: File):
    """Test that SELinux config exists"""
    assert file.is_regular_file("/etc/selinux/config")


@pytest.mark.setting_ids(["GL-SET-cisOS-config-selinux-config-permissive"])
@pytest.mark.feature("cisOS")
def test_cisos_selinux_config_permissive(parse_file: ParseFile):
    """Test that SELinux config has correct content"""
    lines = parse_file.lines("/etc/selinux/config")
    assert "SELINUX=disabled" in lines, "SELINUX should be disabled"


@pytest.mark.setting_ids(["GL-SET-cisOS-config-selinux-config-type"])
@pytest.mark.feature("cisOS")
def test_cisos_selinux_config_type(parse_file: ParseFile):
    """Test that SELinux config has correct content"""
    lines = parse_file.lines("/etc/selinux/config")
    assert "SELINUXTYPE=default" in lines, "SELINUXTYPE should be default"


@pytest.mark.setting_ids(["GL-SET-cisOS-config-selinux-config-setlocaldefs"])
@pytest.mark.feature("cisOS")
def test_cisos_selinux_config_setlocaldefs(parse_file: ParseFile):
    """Test that SELinux config has correct content"""
    lines = parse_file.lines("/etc/selinux/config")
    assert "SETLOCALDEFS=0" in lines, "SETLOCALDEFS should be 0"


@pytest.mark.setting_ids(["GL-SET-cisOS-config-sysstat-sysstat"])
@pytest.mark.feature("cisOS")
def test_cisos_sysstat_config_exists(file: File):
    """Test that sysstat config exists"""
    assert file.is_regular_file("/etc/sysstat/sysstat")


@pytest.mark.setting_ids(["GL-SET-cisOS-config-sysstat-sysstat-umask"])
@pytest.mark.feature("cisOS")
def test_cisos_sysstat_config_umask(parse_file: ParseFile):
    """Test that sysstat config has correct content"""
    lines = parse_file.lines("/etc/sysstat/sysstat")
    assert "UMASK=0027" in lines, "UMASK should be 0027"


@pytest.mark.setting_ids(["GL-SET-cisOS-config-tmpfiles-var"])
@pytest.mark.feature("cisOS")
def test_cisos_tmpfiles_var_exists(file: File):
    """Test that tmpfiles var.conf exists"""
    assert file.is_regular_file("/usr/lib/tmpfiles.d/var.conf")


# =============================================================================
# cisOS Feature - Cron Permissions
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-cisOS-config-cron-d-permissions",
        "GL-SET-cisOS-config-cron-daily-permissions",
        "GL-SET-cisOS-config-cron-hourly-permissions",
        "GL-SET-cisOS-config-cron-monthly-permissions",
        "GL-SET-cisOS-config-cron-weekly-permissions",
        "GL-SET-cisOS-config-crontab-permissions",
        "GL-SET-cisOS-config-cron-users-ownership-and-permissions",
    ]
)
@pytest.mark.feature("cisOS")
def test_cisos_cron_permissions(file: File):
    """Test that cron directories and files have correct permissions"""
    paths_permissions = {
        "/etc/cron.d": "0700",
        "/etc/cron.daily": "0700",
        "/etc/cron.hourly": "0700",
        "/etc/cron.monthly": "0700",
        "/etc/cron.weekly": "0700",
        "/etc/crontab": "0600",
        "/etc/cron.allow": "0600",
        "/etc/at.allow": "0600",
    }

    missing = [
        path
        for path, expected_perms in paths_permissions.items()
        if not file.has_mode(path, expected_perms)
    ]
    assert (
        not missing
    ), f"Cron directories should have permissions {paths_permissions.values()}, but have {missing}"


# =============================================================================
# cisOS Feature - Login & Password Policies
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-cisOS-config-login-defs-password-expire",
        "GL-SET-cisOS-config-login-defs-password-min-days",
    ]
)
@pytest.mark.feature("cisOS")
def test_cisos_login_defs_password_policies(parse_file: ParseFile):
    """Test that login.defs has correct password policies"""
    lines = parse_file.lines("/etc/login.defs")

    assert "PASS_MAX_DAYS 90" in lines, "PASS_MAX_DAYS should be 90"
    assert "PASS_MIN_DAYS 7" in lines, "PASS_MIN_DAYS should be 7"


@pytest.mark.setting_ids(["GL-SET-cisOS-config-security-pwquality"])
@pytest.mark.feature("cisOS")
def test_cisos_pwquality_config_exists(file: File):
    """Test that pwquality.conf exists"""
    assert file.is_regular_file("/etc/security/pwquality.conf")


@pytest.mark.setting_ids(["GL-SET-cisOS-config-security-pwquality"])
@pytest.mark.feature("cisOS")
def test_cisos_pwquality_config_content(parse_file: ParseFile):
    """Test that pwquality.conf has correct content"""
    lines = parse_file.lines("/etc/security/pwquality.conf")
    assert "minlen = 14" in lines, "minlen should be 14"
    assert "dcredit = -1" in lines, "dcredit should be -1"
    assert "ucredit = -1" in lines, "ucredit should be -1"
    assert "ocredit = -1" in lines, "ocredit should be -1"
    assert "lcredit = -1" in lines, "lcredit should be -1"


# =============================================================================
# cisOS Feature - Additional System Configuration
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-cisOS-config-pam-common-password-permissions"])
@pytest.mark.feature("cisOS")
def test_cisos_pam_common_password_permissions(file: File):
    """Test that common-password has correct permissions"""
    path_permissions = {
        "/etc/pam.d/common-password": "0644",
    }
    missing = [
        path
        for path, expected_perms in path_permissions.items()
        if not file.has_mode(path, expected_perms)
    ]
    assert (
        not missing
    ), f"PAM files should have permissions {path_permissions.values()}, but have {missing}"


@pytest.mark.parametrize("pam_config", ["/etc/pam.d/su"], indirect=["pam_config"])
@pytest.mark.setting_ids(["GL-SET-cisOS-config-pam-su-restrict"])
@pytest.mark.feature("cisOS")
def test_cisos_pam_su_restrict(pam_config: PamConfig):
    """Test that su is restricted with pam_wheel.so"""
    wheel_entries = pam_config.find_entries(
        type_="auth", module_contains="pam_wheel.so"
    )
    assert len(wheel_entries) > 0, "pam_wheel.so should be configured in /etc/pam.d/su"


@pytest.mark.setting_ids(["GL-SET-cisOS-config-hosts-allow"])
@pytest.mark.feature("cisOS")
def test_cisos_hosts_allow_exists(file: File):
    """Test that hosts.allow exists"""
    assert file.exists("/etc/hosts.allow")


@pytest.mark.setting_ids(["GL-SET-cisOS-config-hosts-allow"])
@pytest.mark.feature("cisOS")
def test_cisos_hosts_allow_deny_all(parse_file: ParseFile):
    """Test that hosts.allow denies all hosts but localhost"""
    lines = parse_file.lines("/etc/hosts.allow")
    assert "ALL: 127.0.0.1,localhost" in lines, "hosts.allow should allow localhost"
    assert "ALL: ALL" in lines, "hosts.allow should deny all hosts"


@pytest.mark.setting_ids(["GL-SET-cisOS-config-log-file-permissions"])
@pytest.mark.feature("cisOS")
def test_cisos_log_files_permissions(find, file: File):
    """Test that /var/log files have correct permissions"""
    dir = "/var/log"
    find.root_paths = dir
    find.entry_type = "files"
    missing = [file_path for file_path in find if not file.has_mode(file_path, "0640")]
    assert not missing, f"Log files should have permissions 0640, but have {missing}"


@pytest.mark.setting_ids(["GL-SET-cisOS-config-shell-umask"])
@pytest.mark.feature("cisOS")
def test_cisos_shell_umask_configured(parse_file: ParseFile):
    """Test that umask is configured in shell startup files"""
    lines = parse_file.lines("/etc/bash.bashrc")
    assert "umask 077" in lines, "umask 077 should be configured in /etc/bash.bashrc"

    lines = parse_file.lines("/etc/profile")
    assert "umask 077" in lines, "umask 077 should be configured in /etc/profile"


@pytest.mark.setting_ids(["GL-SET-cisOS-config-systemd-journald-storage-persistent"])
@pytest.mark.feature("cisOS")
def test_cisos_journald_storage_persistent(parse_file: ParseFile):
    """Test that journald storage is configured as persistent"""
    lines = parse_file.lines("/etc/systemd/journald.conf")
    assert "Storage=persistent" in lines, "journald.conf should have Storage=persistent"


@pytest.mark.setting_ids(["GL-SET-cisOS-config-udev-rules-usb-devices"])
@pytest.mark.feature("cisOS")
def test_cisos_udev_usb_rules_exist(file: File):
    """Test that udev rules for USB devices exist"""
    usb_rules = "/etc/udev/rules.d/10-CIS_99.2_usb_devices.sh"
    assert file.exists(usb_rules), f"USB device udev rules should exist at {usb_rules}"


@pytest.mark.setting_ids(["GL-SET-cisOS-config-user-root-password"])
@pytest.mark.feature("cisOS")
@pytest.mark.root(reason="Reading shadow file needs root privileges")
def test_cisos_root_password_configured(shadow_entries: List[Shadow]):
    """Test that root password is configured"""
    root_entry = next(
        (entry for entry in shadow_entries if entry.login_name == "root"), None
    )
    assert root_entry, "Root entry should exist"
    assert root_entry.encrypted_password not in [
        "",
        "!",
        "*",
        "!!",
        "!!",
    ], "Root password should be configured (not empty or locked)"
    assert root_entry.encrypted_password.startswith(
        "$"
    ), "Root password should be properly hashed"


# =============================================================================
# cisSshd Feature - CIS SSH Daemon Hardening
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-cisSshd-config-firewall-ipv4-flush",
        "GL-SET-cisSshd-config-firewall-ipv4-gl-default",
        "GL-SET-cisSshd-config-firewall-ipv6-flush",
        "GL-SET-cisSshd-config-firewall-ipv6-gl-default",
    ]
)
@pytest.mark.feature("cisSshd")
def test_cissshd_firewall_configs_exist(file: File):
    """Test that CIS SSHD firewall configurations exist"""
    configs = [
        "/etc/firewall/ipv4_flush.sh",
        "/etc/firewall/ipv4_gl_default.conf",
        "/etc/firewall/ipv6_flush.sh",
        "/etc/firewall/ipv6_gl_default.conf",
    ]
    missing = [cfg for cfg in configs if not file.exists(cfg)]
    assert not missing, f"Missing CIS SSHD firewall configs: {', '.join(missing)}"


@pytest.mark.setting_ids(["GL-SET-cisSshd-config-ssh-sshd-banner"])
@pytest.mark.feature("cisSshd")
def test_cissshd_banner_exists(file: File):
    """Test that CIS SSHD banner exists"""
    assert file.is_regular_file("/etc/ssh/sshd-banner")


@pytest.mark.setting_ids(["GL-SET-cisSshd-config-ssh-sshd-banner"])
@pytest.mark.feature("cisSshd")
def test_cissshd_banner_content(parse_file: ParseFile):
    """Test that CIS SSHD banner content exists"""
    lines = parse_file.lines("/etc/ssh/sshd-banner")
    assert (
        "Authorized uses only. All activity may be monitored and reported." in lines
    ), "sshd banner should contain the correct content"


@pytest.mark.setting_ids(
    [
        "GL-SET-cisSshd-config-ssh-sshd-config-002",
    ]
)
@pytest.mark.feature("cisSshd")
def test_cissshd_sshd_config_exists(file: File):
    """Test that CIS SSHD config exists with proper permissions"""
    assert file.is_regular_file("/etc/ssh/sshd_config")


@pytest.mark.setting_ids(
    [
        "GL-SET-cisSshd-config-ssh-sshd-config-002",
    ]
)
@pytest.mark.feature("cisSshd")
def test_cissshd_sshd_config_content(parse_file: ParseFile):
    """Test that CIS SSHD config content exists"""
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
        "AcceptEnv LANG LC_*",
        "Subsystem sftp /usr/lib/openssh/sftp-server -f AUTHPRIV -l INFO",
        "ClientAliveInterval 300",
        "ClientAliveCountMax 0",
        "AuthenticationMethods publickey",
        "PubkeyAuthentication yes",
        "PasswordAuthentication no",
        "KbdInteractiveAuthentication no",
        "KerberosAuthentication no",
        "ChallengeResponseAuthentication no",
        "GSSAPIAuthentication no",
        "GSSAPIKeyExchange no",
        "LoginGraceTime 60",
        "AllowUsers *",
        "AllowGroups *",
        "DenyUsers nobody",
        "DenyGroups nobody",
        "PermitEmptyPasswords no",
        "PermitUserEnvironment no",
        "HostKey /etc/ssh/ssh_host_ed25519_key",
        "HostKey /etc/ssh/ssh_host_rsa_key",
        "Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr",
        "MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512,hmac-sha2-256",
        "KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org,diffie-hellman-group14-sha256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,ecdh-sha2-nistp521,ecdh-sha2-nistp384,ecdh-sha2-nistp256,diffie-hellman-group-exchange-sha256",
        "RekeyLimit 512M 6h",
        "AllowAgentForwarding no",
        "AllowTcpForwarding no",
        "AllowStreamLocalForwarding no",
        "PermitTunnel no",
        "PermitUserRC no",
        "GatewayPorts no",
        "MaxAuthTries 4",
        "AllowTCPForwarding no",
        "MaxStartups 10:30:60",
        "MaxSessions 10",
        "Banner /etc/issue.net",
    ]


@pytest.mark.setting_ids(["GL-SET-cisSshd-config-ssh-sshd-config-permissions"])
@pytest.mark.feature("cisSshd")
def test_cissshd_sshd_config_permissions(file: File):
    """Test that CIS SSHD config has proper permissions"""
    assert file.has_mode("/etc/ssh/sshd_config", "600")


# =============================================================================
# cis Feature - CIS Baseline Configuration
# =============================================================================


# TODO: check actual /opt/cis-hardening/etc/conf.d/ contents and exceptions
@pytest.mark.setting_ids(
    [
        "GL-SET-cis-config-cis-hardening-disable",
        "GL-SET-cis-config-cis-hardening-exceptions",
    ]
)
@pytest.mark.feature("cis")
def test_cis_hardening_configs_exist(file: File):
    """Test that CIS hardening configuration files exist"""
    # These might be in different locations, checking common paths
    paths = [
        "/etc/cis-hardening.conf",
        "/etc/cis/hardening.conf",
        "/etc/default/cis-hardening",
    ]
    exists = any(file.exists(path) for path in paths)
    assert exists, "CIS hardening configuration should exist"


@pytest.mark.setting_ids(["GL-SET-cis-config-cis-logrotate-permissions"])
@pytest.mark.feature("cis")
def test_cis_logrotate_config_exists(file: File):
    """Test that CIS logrotate configuration exists"""
    assert file.is_regular_file("/etc/logrotate.conf")


@pytest.mark.setting_ids(["GL-SET-cis-config-cis-logrotate-permissions"])
@pytest.mark.feature("cis")
def test_cis_logrotate_permissions(file: File):
    """Test that CIS logrotate configuration exists"""
    assert file.has_mode("/etc/logrotate.conf", "0640")
