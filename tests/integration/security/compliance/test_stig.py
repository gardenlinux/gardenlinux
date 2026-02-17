import pytest
from plugins.file import File
from plugins.kernel_module import KernelModule
from plugins.parse_file import ParseFile

# =============================================================================
# stig Feature - Security Technical Implementation Guide
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-stig-config-audit-auditd-conf",
        "GL-SET-stig-config-audit-rules-d-stig-rules",
    ]
)
@pytest.mark.feature("stig")
def test_stig_audit_configs_exist(file: File):
    """Test that STIG audit configurations exist"""
    configs = [
        "/etc/audit/auditd.conf",
        "/etc/audit/rules.d/stig.rules",
    ]
    missing = [cfg for cfg in configs if not file.is_regular_file(cfg)]
    assert not missing, f"Missing STIG audit configs: {', '.join(missing)}"


@pytest.mark.setting_ids(["GL-SET-stig-config-audit-auditd-conf"])
@pytest.mark.feature("stig")
def test_stig_audit_auditd_conf_content(parse_file: ParseFile):
    """Test that STIG audit auditd.conf content exists"""
    lines = parse_file.lines("/etc/audit/auditd.conf")
    assert (
        "space_left_action email" in lines
    ), "auditd.conf should contain the correct content"
    assert (
        "space_left 250000" in lines
    ), "auditd.conf should contain the correct content"
    assert (
        "action_mail_acct root@localhost" in lines
    ), "auditd.conf should contain the correct content"


@pytest.mark.setting_ids(["GL-SET-stig-config-audit-rules-d-stig-rules"])
@pytest.mark.feature("stig")
def test_stig_audit_rules_d_stig_rules_content(parse_file: ParseFile):
    """Test that STIG audit rules.d/stig.rules content exists"""
    lines = parse_file.lines("/etc/audit/rules.d/stig.rules")
    assert lines == [
        "-a always,exit -F path=/usr/bin/ssh-agent -F perm=x -F auid>=1000 -F auid!=4294967295 -k privileged-ssh",
        "-a always,exit -F path=/usr/lib/openssh/ssh-keysign -F perm=x -F auid>=1000 -F auid!=4294967295 -k privileged-ssh",
        "-a always,exit -F path=/usr/bin/chacl -F perm=x -F auid>=1000 -F auid!=4294967295 -k perm_chng",
        "-w /var/log/tallylog -p wa -k logins",
        "-w /var/log/faillog -p wa -k logins",
        "-w /var/log/lastlog -p wa -k logins",
        "-a always,exit -F path=/usr/bin/newgrp -F perm=x -F auid>=1000 -F auid!=4294967295 -k priv_cmd",
        "-a always,exit -F path=/usr/bin/chcon -F perm=x -F auid>=1000 -F auid!=4294967295 -k perm_chng",
        "-a always,exit -F path=/usr/bin/setfacl -F perm=x -F auid>=1000 -F auid!=4294967295 -k perm_chng",
        "-a always,exit -F path=/usr/bin/passwd -F perm=x -F auid>=1000 -F auid!=4294967295 -k privileged-passwd",
        "-a always,exit -F path=/sbin/unix_update -F perm=x -F auid>=1000 -F auid!=4294967295 -k privileged-unix-update",
        "-a always,exit -F arch=b32 -S delete_module -F auid>=1000 -F auid!=4294967295 -k module_chng",
        "-a always,exit -F arch=b64 -S delete_module -F auid>=1000 -F auid!=4294967295 -k module_chng",
        "-a always,exit -F arch=b32 -S init_module,finit_module -F auid>=1000 -F auid!=4294967295 -k module_chng",
        "-a always,exit -F arch=b64 -S init_module,finit_module -F auid>=1000 -F auid!=4294967295 -k module_chng",
        "-a always,exit -F path=/usr/sbin/pam_timestamp_check -F perm=x -F auid>=1000 -F auid!=4294967295 -k privileged-pam_timestamp_check",
        "-a always,exit -F path=/usr/bin/crontab -F perm=x -F auid>=1000 -F auid!=4294967295 -k privileged-crontab",
        "-a always,exit -F path=/usr/sbin/usermod -F perm=x -F auid>=1000 -F auid!=4294967295 -k privileged-usermod",
        "-a always,exit -F path=/usr/bin/chage -F perm=x -F auid>=1000 -F auid!=4294967295 -k privileged-chage",
        "-a always,exit -F path=/usr/bin/gpasswd -F perm=x -F auid>=1000 -F auid!=4294967295 -k privileged-gpasswd",
        "-w /etc/passwd -p wa -k usergroup_modification",
        "-w /etc/group -p wa -k usergroup_modification",
        "-w /usr/sbin/fdisk -p x -k fdisk",
        "-w /etc/shadow -p wa -k usergroup_modification",
        "-w /etc/gshadow -p wa -k usergroup_modification",
        "-w /etc/security/opasswd -p wa -k usergroup_modification",
        "-a always,exit -F arch=b64 -S unlink,unlinkat,rename,renameat,rmdir -F auid>=1000 -F auid!=4294967295 -k delete",
        "-a always,exit -F arch=b32 -S unlink,unlinkat,rename,renameat,rmdir -F auid>=1000 -F auid!=4294967295 -k delete",
        "-w /var/run/utmp -p wa -k logins",
        "-w /var/log/btmp -p wa -k logins",
        "-w /var/log/wtmp -p wa -k logins",
        "-w /sbin/modprobe -p x -k modules",
        "-w /bin/kmod -p x -k modules",
        "-a always,exit -F path=/usr/bin/chfn -F perm=x -F auid>=1000 -F auid!=4294967295 -k privileged-chfn",
        "-a always,exit -F path=/bin/su -F perm=x -F auid>=1000 -F auid!=4294967295 -k privileged-priv_change",
        "-a always,exit -F path=/usr/lib/openssh/ssh-keysign -F perm=x -F auid>=1000 -F auid!=4294967295 -k privileged-ssh",
        "-a always,exit -F path=/usr/bin/ssh-agent -F perm=x -F auid>=1000 -F auid!=4294967295 -k privileged-ssh",
        "-a always,exit -F path=/usr/bin/umount -F perm=x -F auid>=1000 -F auid!=4294967295 -k privileged-umount",
        "-a always,exit -F path=/usr/bin/mount -F perm=x -F auid>=1000 -F auid!=4294967295 -k privileged-mount",
        "-a always,exit -F arch=b32 -S setxattr,fsetxattr,lsetxattr,removexattr,fremovexattr,lremovexattr -F auid>=1000 -F auid!=4294967295 -k perm_mod",
        "-a always,exit -F arch=b32 -S setxattr,fsetxattr,lsetxattr,removexattr,fremovexattr,lremovexattr -F auid=0 -k perm_mod",
        "-a always,exit -F arch=b64 -S setxattr,fsetxattr,lsetxattr,removexattr,fremovexattr,lremovexattr -F auid>=1000 -F auid!=4294967295 -k perm_mod",
        "-a always,exit -F arch=b64 -S setxattr,fsetxattr,lsetxattr,removexattr,fremovexattr,lremovexattr -F auid=0 -k perm_mod",
        "-a always,exit -F arch=b64 -S execve -C uid!=euid -F euid=0 -F key=execpriv",
        "-a always,exit -F arch=b64 -S execve -C gid!=egid -F egid=0 -F key=execpriv",
        "-a always,exit -F arch=b32 -S execve -C uid!=euid -F euid=0 -F key=execpriv",
        "-a always,exit -F arch=b32 -S execve -C gid!=egid -F egid=0 -F key=execpriv",
        "-w /var/log/sudo.log -p wa -k maintenance",
        "-a always,exit -F arch=b32 -S chown,fchown,fchownat,lchown -F auid>=1000 -F auid!=4294967295 -k perm_chng",
        "-a always,exit -F arch=b64 -S chown,fchown,fchownat,lchown -F auid>=1000 -F auid!=4294967295 -k perm_chng",
        "-a always,exit -F arch=b32 -S chmod,fchmod,fchmodat -F auid>=1000 -F auid!=4294967295 -k perm_chng",
        "-a always,exit -F arch=b64 -S chmod,fchmod,fchmodat -F auid>=1000 -F auid!=4294967295 -k perm_chng",
        "-a always,exit -F path=/usr/bin/chsh -F perm=x -F auid>=1000 -F auid!=4294967295 -k priv_cmd",
        "-a always,exit -F path=/usr/bin/sudoedit -F perm=x -F auid>=1000 -F auid!=4294967295 -k priv_cmd",
        "-a always,exit -F arch=b32 -S creat,open,openat,open_by_handle_at,truncate,ftruncate -F exit=-EPERM -F auid>=1000 -F auid!=4294967295 -k perm_access",
        "-a always,exit -F arch=b32 -S creat,open,openat,open_by_handle_at,truncate,ftruncate -F exit=-EACCES -F auid>=1000 -F auid!=4294967295 -k perm_access",
        "-a always,exit -F arch=b64 -S creat,open,openat,open_by_handle_at,truncate,ftruncate -F exit=-EPERM -F auid>=1000 -F auid!=4294967295 -k perm_access",
        "-a always,exit -F arch=b64 -S creat,open,openat,open_by_handle_at,truncate,ftruncate -F exit=-EACCES -F auid>=1000 -F auid!=4294967295 -k perm_access",
        "-a always,exit -F path=/usr/bin/sudo -F perm=x -F auid>=1000 -F auid!=4294967295 -k priv_cmd",
        "-w /var/log/sudo.log -p wa -k maintenance",
        "-a always,exit -F arch=b32 -S chown,fchown,fchownat,lchown -F auid>=1000 -F auid!=4294967295 -k perm_chng",
        "-a always,exit -F arch=b64 -S chown,fchown,fchownat,lchown -F auid>=1000 -F auid!=4294967295 -k perm_chng",
        "-a always,exit -F arch=b32 -S chmod,fchmod,fchmodat -F auid>=1000 -F auid!=4294967295 -k perm_chng",
        "-a always,exit -F arch=b64 -S chmod,fchmod,fchmodat -F auid>=1000 -F auid!=4294967295 -k perm_chng",
        "-a always,exit -F path=/usr/bin/chsh -F perm=x -F auid>=1000 -F auid!=4294967295 -k priv_cmd",
        "-a always,exit -F path=/usr/bin/sudoedit -F perm=x -F auid>=1000 -F auid!=4294967295 -k priv_cmd",
        "-a always,exit -F arch=b32 -S creat,open,openat,open_by_handle_at,truncate,ftruncate -F exit=-EPERM -F auid>=1000 -F auid!=4294967295 -k perm_access",
        "-a always,exit -F arch=b32 -S creat,open,openat,open_by_handle_at,truncate,ftruncate -F exit=-EACCES -F auid>=1000 -F auid!=4294967295 -k perm_access",
        "-a always,exit -F arch=b64 -S creat,open,openat,open_by_handle_at,truncate,ftruncate -F exit=-EPERM -F auid>=1000 -F auid!=4294967295 -k perm_access",
        "-a always,exit -F arch=b64 -S creat,open,openat,open_by_handle_at,truncate,ftruncate -F exit=-EACCES -F auid>=1000 -F auid!=4294967295 -k perm_access",
        "-a always,exit -F path=/usr/bin/sudo -F perm=x -F auid>=1000 -F auid!=4294967295 -k priv_cmd",
    ]


@pytest.mark.setting_ids(["GL-SET-stig-config-kernel-cmdline-audit"])
@pytest.mark.feature("stig")
def test_stig_kernel_cmdline_audit_exists(file: File):
    """Test that STIG audit kernel cmdline config exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/90-audit.cfg")


@pytest.mark.setting_ids(["GL-SET-stig-config-kernel-cmdline-audit"])
@pytest.mark.feature("stig")
def test_stig_kernel_cmdline_audit_content(parse_file: ParseFile):
    """Test that STIG audit kernel cmdline config content exists"""
    lines = parse_file.lines("/etc/kernel/cmdline.d/90-audit.cfg")
    assert (
        "audit=1" in lines
    ), "kernel cmdline audit configuration should contain the correct content"


@pytest.mark.setting_ids(["GL-SET-stig-config-modprobe-usb-disable"])
@pytest.mark.feature("stig")
def test_stig_usb_disabled(file: File):
    """Test that USB is disabled via modprobe"""
    assert file.is_regular_file("/etc/modprobe.d/disabled_usb.conf")


@pytest.mark.setting_ids(["GL-SET-stig-config-modprobe-usb-disable"])
@pytest.mark.feature("stig")
@pytest.mark.booted(reason="Modules can only be loaded on booted system")
def test_stig_modprobe_disable_modules_not_loaded(kernel_module: KernelModule):
    """Test that disabled modules are not loaded"""
    modules = [
        "usbcore",
        "usb-common",
        "usb-storage",
    ]
    for module in modules:
        assert not kernel_module.is_module_loaded(
            module
        ), f"Module {module} is loaded but should be deny listed"


@pytest.mark.setting_ids(
    [
        "GL-SET-stig-config-security-faillock",
        "GL-SET-stig-config-security-limits",
        "GL-SET-stig-config-security-pwquality",
    ]
)
@pytest.mark.feature("stig")
def test_stig_security_configs_exist(file: File):
    """Test that STIG security configurations exist"""
    configs = [
        "/etc/security/faillock.conf",
        "/etc/security/limits.conf",
        "/etc/security/pwquality.conf",
    ]
    missing = [cfg for cfg in configs if not file.is_regular_file(cfg)]
    assert not missing, f"Missing STIG security configs: {', '.join(missing)}"


@pytest.mark.setting_ids(["GL-SET-stig-config-security-faillock"])
@pytest.mark.feature("stig")
def test_stig_security_faillock_content(parse_file: ParseFile):
    """Test that STIG security faillock configuration content exists"""
    lines = parse_file.lines("/etc/security/faillock.conf")
    assert "audit" in lines, "faillock configuration should contain the correct content"
    assert (
        "silent" in lines
    ), "faillock configuration should contain the correct content"
    assert (
        "deny = 3" in lines
    ), "faillock configuration should contain the correct content"
    assert (
        "fail_interval = 900" in lines
    ), "faillock configuration should contain the correct content"
    assert (
        "unlock_time = 0" in lines
    ), "faillock configuration should contain the correct content"


@pytest.mark.setting_ids(["GL-SET-stig-config-apt-vendor-ubuntu"])
@pytest.mark.feature("stig")
def test_stig_apt_vendor_ubuntu_exists(file: File):
    """Test that STIG APT vendor config exists"""
    assert file.exists("/etc/apt/apt.conf.d/01-vendor-ubuntu")


@pytest.mark.setting_ids(["GL-SET-stig-config-apt-vendor-ubuntu"])
@pytest.mark.feature("stig")
def test_stig_apt_vendor_ubuntu_content(parse_file: ParseFile):
    """Test that STIG APT vendor config content exists"""
    lines = parse_file.lines("/etc/apt/apt.conf.d/01-vendor-ubuntu")
    assert (
        'APT::Get::AllowUnauthenticated "false";' in lines
    ), "APT vendor config should contain the correct content"


@pytest.mark.setting_ids(["GL-SET-stig-config-rsyslog-default"])
@pytest.mark.feature("stig")
def test_stig_rsyslog_default_exists(file: File):
    """Test that STIG rsyslog default config exists"""
    assert file.is_regular_file("/etc/rsyslog.d/50-default.conf")


@pytest.mark.setting_ids(["GL-SET-stig-config-rsyslog-default"])
@pytest.mark.feature("stig")
def test_stig_rsyslog_default_content(parse_file: ParseFile):
    """Test that STIG rsyslog default config content exists"""
    lines = parse_file.lines("/etc/rsyslog.d/50-default.conf")
    assert (
        "auth.*,authpriv.* /var/log/secure" in lines
    ), "rsyslog default config should contain the correct content"
    assert (
        "daemon.* /var/log/messages" in lines
    ), "rsyslog default config should contain the correct content"
