import pytest

"""
Ref: SRG-OS-000057-GPOS-00027, SRG-OS-000120-GPOS-00061,
     SRG-OS-000122-GPOS-00063, SRG-OS-000329-GPOS-00128

Verify the operating system protects audit logs, uses SHA512 as the password
hashing algorithm, enables the audit daemon, and automatically locks an account
after three consecutive invalid logon attempts.
"""

AUDITD_CONF = "/etc/audit/auditd.conf"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-service-auditd-enable"])
@pytest.mark.feature(
    "disaSTIGmedium", reason="auditd service is enabled by disaSTIGmedium"
)
@pytest.mark.booted(reason="requires systemd")
def test_auditd_service_is_enabled(systemd) -> None:
    assert systemd.is_enabled("auditd"), "stigcompliance: auditd.service is not enabled"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-audit-auditd-conf"])
@pytest.mark.feature(
    "disaSTIGmedium", reason="auditd log_group is set to root by disaSTIGmedium"
)
def test_auditd_conf_log_group_is_root(parse_file) -> None:
    config = parse_file.parse(AUDITD_CONF, format="keyval")
    assert config["log_group"] == "root", (
        f"stigcompliance: log_group in {AUDITD_CONF} is "
        f"{config['log_group']!r}, expected 'root'"
    )


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-login-defs-encrypt"])
@pytest.mark.feature(
    "disaSTIGmedium", reason="SHA512 password hashing is configured by disaSTIGmedium"
)
def test_login_defs_encrypt_method_is_sha512(parse_file) -> None:
    config = parse_file.parse("/etc/login.defs", format="spacedelim")
    assert config["ENCRYPT_METHOD"] == "SHA512", (
        f"stigcompliance: ENCRYPT_METHOD in /etc/login.defs is "
        f"{config['ENCRYPT_METHOD']!r}, expected 'SHA512'"
    )


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGlow-config-security-faillock"])
@pytest.mark.feature(
    "disaSTIGlow", reason="faillock deny threshold is configured by disaSTIGlow"
)
def test_faillock_deny_is_3(parse_file) -> None:
    config = parse_file.parse("/etc/security/faillock.conf", format="keyval")
    assert (
        config["deny"] == "3"
    ), f"stigcompliance: deny in /etc/security/faillock.conf is {config['deny']!r}, expected '3'"


@pytest.mark.testcov(
    ["GL-TESTCOV-disaSTIGmedium-config-audit-rules-d-90-finalize-rules"]
)
@pytest.mark.feature(
    "disaSTIGmedium",
    reason="audit rules are made immutable by disaSTIGmedium via 90-finalize.rules",
)
@pytest.mark.booted(reason="requires running audit subsystem")
@pytest.mark.root(reason="requires access to audit status")
def test_audit_rules_are_immutable(shell) -> None:
    result = shell("auditctl -s", capture_output=True, ignore_exit_code=True)
    assert (
        "enabled 2" in result.stdout
    ), "stigcompliance: audit rules are not immutable (expected 'enabled 2' in auditctl -s output)"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-audit-rules-service-override"])
@pytest.mark.feature(
    "disaSTIGmedium",
    reason="audit-rules.service override is provided by disaSTIGmedium",
)
def test_audit_rules_service_override_exists(file) -> None:
    assert file.exists(
        "/etc/systemd/system/audit-rules.service.d/override.conf"
    ), "stigcompliance: audit-rules.service.d/override.conf is missing"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-journal-permissions"])
@pytest.mark.feature(
    "disaSTIGmedium",
    reason="journal directory permissions are set by disaSTIGmedium",
)
def test_systemd_journal_is_not_world_readable(file) -> None:
    assert file.has_permissions(
        "/var/log/journal", "rwxr-s---"
    ), "stigcompliance: /var/log/journal does not have expected permissions rwxr-s---"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-getty-no-autologin"])
@pytest.mark.feature(
    "disaSTIGmedium",
    reason="getty autologin is disabled by disaSTIGmedium",
)
def test_getty_no_autologin_override_exists(file) -> None:
    assert file.exists(
        "/etc/systemd/system/getty@.service.d/no-autologin.conf"
    ), "stigcompliance: getty no-autologin override is missing"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-pam-common-auth-faildelay"])
@pytest.mark.feature(
    "disaSTIGmedium",
    reason="pam_faildelay is configured by disaSTIGmedium",
)
def test_pam_faildelay_is_configured(parse_file) -> None:
    assert "auth required pam_faildelay.so delay=4000000" in parse_file.lines(
        "/etc/pam.d/common-auth"
    ), "stigcompliance: pam_faildelay delay=4000000 not found in /etc/pam.d/common-auth"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-pam-garden-disaSTIG"])
@pytest.mark.feature(
    "disaSTIGmedium",
    reason="garden-disaSTIG pam config is shipped by disaSTIGmedium",
)
def test_pam_garden_disastig_config_exists(file) -> None:
    assert file.exists(
        "/usr/share/pam-configs/garden-disaSTIG"
    ), "stigcompliance: /usr/share/pam-configs/garden-disaSTIG is missing"
