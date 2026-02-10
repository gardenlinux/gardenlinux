from math import e
from mimetypes import init

import pytest
from plugins.file import File
from plugins.parse_file import ParseFile

# =============================================================================
# sap Feature - SAP Compliance Requirements
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-sap-config-audit-rules-privilege-escalaction-permissions",
    ]
)
@pytest.mark.feature("sap")
def test_sap_audit_privilege_escalation_permissions(file: File):
    """Test that SAP has privilege escalation audit rules permissions"""
    assert file.has_mode(
        "/etc/audit/rules.d/70-privilege-escalation.rules", "0640"
    ), "SAP privilege escalation audit rules should have 0640 permissions"


@pytest.mark.setting_ids(
    [
        "GL-SET-sap-config-audit-rules-privilege-escalaction",
    ]
)
@pytest.mark.feature("sap")
def test_sap_audit_privilege_escalation(parse_file: ParseFile):
    """Test that SAP has privilege escalation audit rules"""
    expected_lines = [
        "-a exit,always -F arch=b64 -S setuid -S setreuid -S setgid -S setregid -F auid>0 -F auid!=-1 -F key=privilege_escalation",
        "-a exit,always -F arch=b32 -S setuid -S setreuid -S setgid -S setregid -F auid>0 -F auid!=-1 -F key=privilege_escalation",
        "-a exit,always -F arch=b64 -S execve -S execveat -F euid=0 -F auid>0 -F auid!=-1 -F key=privilege_escalation",
        "-a exit,always -F arch=b32 -S execve -S execveat -F euid=0 -F auid>0 -F auid!=-1 -F key=privilege_escalation",
    ]
    assert expected_lines in parse_file.lines(
        "/etc/audit/rules.d/70-privilege-escalation.rules"
    ), "SAP privilege escalation audit rules should be correct"


@pytest.mark.setting_ids(
    [
        "GL-SET-sap-config-audit-rules-privileged-special-permissions",
    ]
)
@pytest.mark.feature("sap")
def test_sap_audit_privilege_escalation_special_permissions(file: File):
    """Test that SAP has privilege escalation audit rules special permissions"""
    assert file.has_mode(
        "/etc/audit/rules.d/70-privileged-special.rules", "0640"
    ), "SAP privilege escalation audit rules special should have 0640 permissions"


@pytest.mark.setting_ids(
    [
        "GL-SET-sap-config-audit-rules-privileged-special-amd64",
    ]
)
@pytest.mark.feature("sap")
@pytest.mark.arch("amd64")
def test_sap_audit_privilege_escalation_special_amd64(parse_file: ParseFile):
    """Test that SAP has AMD64-specific privilege escalation audit rules"""
    expected_lines = [
        "-a exit,always -F arch=b64 -S mount -S mount_setattr -S umount2 -S mknod -S mknodat -S chroot -F auid!=-1 -F key=privileged_special",
        "-a exit,always -F arch=b32 -S mount -S mount_setattr -S umount2 -S mknod -S mknodat -S chroot -F auid!=-1 -F key=privileged_special",
    ]
    assert expected_lines in parse_file.lines(
        "/etc/audit/rules.d/70-privileged-special.rules"
    ), "SAP AMD64 privilege escalation audit rules should be correct"


@pytest.mark.setting_ids(
    [
        "GL-SET-sap-config-audit-rules-privileged-special-arm64",
    ]
)
@pytest.mark.feature("sap")
@pytest.mark.arch("arm64")
def test_sap_audit_privilege_escalation_special_arm64(parse_file: ParseFile):
    """Test that SAP has ARM64-specific privilege escalation audit rules"""
    expected_lines = [
        "-a exit,always -F arch=b64 -S mount -S mount_setattr -S umount2 -S mknodat -S chroot -F auid!=-1 -F key=privileged_special",
        "-a exit,always -F arch=b32 -S mount -S mount_setattr -S umount2 -S mknodat -S chroot -F auid!=-1 -F key=privileged_special",
    ]
    assert expected_lines in parse_file.lines(
        "/etc/audit/rules.d/70-privileged-special.rules"
    ), "SAP ARM64 privilege escalation audit rules should be correct"


@pytest.mark.setting_ids(
    [
        "GL-SET-sap-config-audit-rules-system-integrity-permissions",
    ]
)
@pytest.mark.feature("sap")
def test_sap_audit_system_integrity_permissions(file: File):
    """Test that SAP has system integrity audit rules with correct permissions"""
    assert file.has_mode(
        "/etc/audit/rules.d/70-system-integrity.rules", "0640"
    ), "SAP system integrity audit rules should have 0640 permissions"


@pytest.mark.setting_ids(
    [
        "GL-SET-sap-config-audit-rules-system-integrity",
    ]
)
@pytest.mark.feature("sap")
def test_sap_audit_system_integrity(parse_file: ParseFile):
    """Test that SAP has system integrity audit rules"""
    expected_lines = [
        "-a exit,always -F dir=/boot -F perm=wa -F key=system_integrity",
        "-a exit,always -F dir=/etc -F perm=wa -F key=system_integrity",
        "-a exit,always -F dir=/bin -F perm=wa -F key=system_integrity",
        "-a exit,always -F dir=/sbin -F perm=wa -F key=system_integrity",
        "-a exit,always -F dir=/usr -F perm=wa -F key=system_integrity",
        "-a exit,always -F dir=/opt -F perm=wa -F key=system_integrity",
        "-a exit,always -F dir=/root -F perm=wa -F key=system_integrity",
        "-a exit,always -F dir=/lib -F perm=wa -F key=system_integrity",
        "#-a exit,always -F dir=/lib64 -F perm=wa -F key=system_integrity",
    ]
    assert expected_lines in parse_file.lines(
        "/etc/audit/rules.d/70-system-integrity.rules"
    ), "SAP system integrity audit rules should be correct"


@pytest.mark.setting_ids(
    [
        "GL-SET-sap-config-issue",
    ]
)
@pytest.mark.feature("sap")
def test_sap_issue_banner_exists(file: File):
    """Test that SAP has issue banner file"""
    assert file.exists("/etc/issue"), "SAP issue banner should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-sap-config-issue",
    ]
)
@pytest.mark.feature("sap")
def test_sap_issue_banner_content(parse_file: ParseFile):
    """Test that SAP has issue banner file"""
    expected_lines = [
        "You are accessing SAP computer systems and network through which you may have access to business sensitive information (“SAP Systems”). SAP Systems are intended for legitimate business use by authorized users of SAP only. Personal use of the SAP Systems you are about to access is not permitted."
    ]
    assert expected_lines in parse_file.lines(
        "/etc/issue"
    ), "SAP issue banner should be correct"


@pytest.mark.setting_ids(
    [
        "GL-SET-sap-config-issue-net",
    ]
)
@pytest.mark.feature("sap")
def test_sap_issue_net_banner_exists(file: File):
    """Test that SAP has network issue banner file"""
    assert file.exists("/etc/issue.net"), "SAP network issue banner should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-sap-config-issue-net",
    ]
)
@pytest.mark.feature("sap")
def test_sap_issue_net_banner_content(parse_file: ParseFile):
    """Test that SAP has network issue banner file"""
    expected_lines = [
        "You are accessing SAP computer systems and network through which you may have access to business sensitive information (“SAP Systems”). SAP Systems are intended for legitimate business use by authorized users of SAP only. Personal use of the SAP Systems you are about to access is not permitted."
    ]
    assert expected_lines in parse_file.lines(
        "/etc/issue.net"
    ), "SAP network issue banner should be correct"


@pytest.mark.setting_ids(
    [
        "GL-SET-sap-config-motd",
    ]
)
@pytest.mark.feature("sap")
def test_sap_motd_exists(file: File):
    """Test that SAP has message of the day file"""
    assert file.exists("/etc/motd"), "SAP motd should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-sap-config-motd",
    ]
)
@pytest.mark.feature("sap")
def test_sap_motd_content(parse_file: ParseFile):
    """Test that SAP has message of the day file"""
    expected_lines = [
        "You are accessing SAP computer systems and network through which you may have access to business sensitive information (“SAP Systems”). SAP Systems are intended for legitimate business use by authorized users of SAP only. Personal use of the SAP Systems you are about to access is not permitted."
    ]
    assert expected_lines in parse_file.lines("/etc/motd"), "SAP motd should be correct"


@pytest.mark.setting_ids(
    [
        "GL-SET-sap-config-tmpfiles-legacy",
    ]
)
@pytest.mark.feature("sap")
def test_sap_tmpfiles_legacy_exists(file: File):
    """Test that SAP has tmpfiles legacy configuration"""
    assert file.exists(
        "/etc/tmpfiles.d/legacy.conf"
    ), "SAP tmpfiles legacy configuration should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-sap-config-tmpfiles-legacy",
    ]
)
@pytest.mark.feature("sap")
def test_sap_tmpfiles_legacy_content(parse_file: ParseFile):
    """Test that SAP has tmpfiles legacy configuration"""
    expected_lines = [
        "L /var/lock - - - - ../run/lock",
        "d /run/lock/subsys 0755 root root -",
        "r! /forcefsck",
        "r! /fastboot",
        "r! /forcequotacheck",
    ]
    assert expected_lines in parse_file.lines(
        "/etc/tmpfiles.d/legacy.conf"
    ), "SAP tmpfiles legacy configuration should be correct"


@pytest.mark.setting_ids(
    [
        "GL-SET-sap-config-security-sap-global-root-ca",
    ]
)
@pytest.mark.feature("sap")
def test_sap_global_root_ca_exists(file: File):
    """Test that SAP Global Root CA certificate exists"""
    assert file.exists(
        "/usr/local/share/ca-certificates/SAP_Global_Root_CA.crt"
    ), "SAP Global Root CA certificate should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-sap-config-security-sap-global-root-ca",
    ]
)
@pytest.mark.feature("sap")
def test_sap_global_root_ca_content(parse_file: ParseFile):
    """Test that SAP Global Root CA certificate content is correct"""
    expected_lines = [
        "-----BEGIN CERTIFICATE-----",
        "MIIGTDCCBDSgAwIBAgIQXQPZPTFhXY9Iizlwx48bmTANBgkqhkiG9w0BAQsFADBO",
        "MQswCQYDVQQGEwJERTERMA8GA1UEBwwIV2FsbGRvcmYxDzANBgNVBAoMBlNBUCBB",
        "RzEbMBkGA1UEAwwSU0FQIEdsb2JhbCBSb290IENBMB4XDTEyMDQyNjE1NDE1NVoX",
        "DTMyMDQyNjE1NDYyN1owTjELMAkGA1UEBhMCREUxETAPBgNVBAcMCFdhbGxkb3Jm",
        "MQ8wDQYDVQQKDAZTQVAgQUcxGzAZBgNVBAMMElNBUCBHbG9iYWwgUm9vdCBDQTCC",
        "AiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAOrxJKFFA1eTrZg1Ux8ax6n/",
        "LQRHZlgLc2FZpfyAgwvkt71wLkPLiTOaRb3Bd1dyydpKcwJLy0dzGkunzNkPRSFz",
        "bKy2IPS0RS45hUCCPzhGnqQM6TcDYWeWpSUvygqujgb/cAG0mSJpvzAD3SMDQ+VJ",
        "Az5Ryq4IrP7LkfCb63LKZxLsHEkEcNKoGPsSsd4LTwuEIyM3ZHcCoA97m6hvgLWV",
        "GLzLIQMEblkswqX29z7JZH+zJopoqZB6eEogE2YpExkw52PufytEslDY3dyVubjp",
        "GlvD4T03F2zm6CYleMwgWbATLVYvk2I9WfqPAP+ln2IU9DZzegSMTWHCE+jizaiq",
        "b5f5s7m8f+cz7ndHSrz8KD/S9iNdWpuSlknHDrh+3lFTX/uWNBRs5mC/cdejcqS1",
        "v6erflyIfqPWWO6PxhIs49NL9Lix3ou6opJo+m8K757T5uP/rQ9KYALIXvl2uFP7",
        "0CqI+VGfossMlSXa1keagraW8qfplz6ffeSJQWO/+zifbfsf0tzUAC72zBuO0qvN",
        "E7rSbqAfpav/o010nKP132gbkb4uOkUfZwCuvZjA8ddsQ4udIBRj0hQlqnPLJOR1",
        "PImrAFC3PW3NgaDEo9QAJBEp5jEJmQghNvEsmzXgABebwLdI9u0VrDz4mSb6TYQC",
        "XTUaSnH3zvwAv8oMx7q7AgMBAAGjggEkMIIBIDAOBgNVHQ8BAf8EBAMCAQYwEgYD",
        "VR0TAQH/BAgwBgEB/wIBATAdBgNVHQ4EFgQUg8dB/Q4mTynBuHmOhnrhv7XXagMw",
        "gdoGA1UdIASB0jCBzzCBzAYKKwYBBAGFNgRkATCBvTAmBggrBgEFBQcCARYaaHR0",
        "cDovL3d3dy5wa2kuY28uc2FwLmNvbS8wgZIGCCsGAQUFBwICMIGFHoGCAEMAZQBy",
        "AHQAaQBmAGkAYwBhAHQAZQAgAFAAbwBsAGkAYwB5ACAAYQBuAGQAIABDAGUAcgB0",
        "AGkAZgBpAGMAYQB0AGkAbwBuACAAUAByAGEAYwB0AGkAYwBlACAAUwB0AGEAdABl",
        "AG0AZQBuAHQAIABvAGYAIABTAEEAUAAgAEEARzANBgkqhkiG9w0BAQsFAAOCAgEA",
        "0HpCIaC36me6ShB3oHDexA2a3UFcU149nZTABPKT+yUCnCQPzvK/6nJUc5I4xPfv",
        "2Q8cIlJjPNRoh9vNSF7OZGRmWQOFFrPWeqX5JA7HQPsRVURjJMeYgZWMpy4t1Tof",
        "lF13u6OY6xV6A5kQZIISFj/dOYLT3+O7wME5SItL+YsNh6BToNU0xAZt71Z8JNdY",
        "VJb2xSPMzn6bNXY8ioGzHlVxfEvzMqebV0KY7BTXR3y/Mh+v/RjXGmvZU6L/gnU7",
        "8mTRPgekYKY8JX2CXTqgfuW6QSnJ+88bHHMhMP7nPwv+YkPcsvCPBSY08ykzFATw",
        "SNoKP1/QFtERVUwrUXt3Cufz9huVysiy23dEyfAglgCCRWA+ZlaaXfieKkUWCJaE",
        "Kw/2Jqz02HDc7uXkFLS1BMYjr3WjShg1a+ulYvrBhNtseRoZT833SStlS/jzZ8Bi",
        "c1dt7UOiIZCGUIODfcZhO8l4mtjh034hdARLF0sUZhkVlosHPml5rlxh+qn8yJiJ",
        "GJ7CUQtNCDBVGksVlwew/+XnesITxrDjUMu+2297at7wjBwCnO93zr1/wsx1e2Um",
        "Xn+IfM6K/pbDar/y6uI9rHlyWu4iJ6cg7DAPJ2CCklw/YHJXhDHGwheO/qSrKtgz",
        "PGHZoN9jcvvvWDLUGtJkEotMgdFpEA2XWR83H4fVFVc=",
        "-----END CERTIFICATE-----",
    ]
    assert expected_lines in parse_file.lines(
        "/usr/local/share/ca-certificates/SAP_Global_Root_CA.crt"
    ), "SAP Global Root CA certificate content should be correct"
