import pytest

"""
Ref: SRG-OS-000057-GPOS-00027, SRG-OS-000075-GPOS-00043,
     SRG-OS-000076-GPOS-00044, SRG-OS-000120-GPOS-00061,
     SRG-OS-000122-GPOS-00063, SRG-OS-000329-GPOS-00128

Verify the operating system protects audit logs, uses SHA512 as the password
hashing algorithm, enables the audit daemon, automatically locks an account
after three consecutive invalid logon attempts, and enforces minimum and
maximum password age.
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


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-security-faillock"])
@pytest.mark.feature(
    "disaSTIGmedium", reason="faillock deny threshold is configured by disaSTIGmedium"
)
def test_faillock_deny_is_3(parse_file) -> None:
    config = parse_file.parse("/etc/security/faillock.conf", format="keyval")
    assert (
        config["deny"] == "3"
    ), f"stigcompliance: deny in /etc/security/faillock.conf is {config['deny']!r}, expected '3'"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-login-defs-pass-min-days"])
@pytest.mark.feature(
    "disaSTIGmedium", reason="PASS_MIN_DAYS is set to 1 by disaSTIGmedium"
)
def test_login_defs_pass_min_days_is_1(parse_file) -> None:
    config = parse_file.parse("/etc/login.defs", format="spacedelim")
    assert config["PASS_MIN_DAYS"] == "1", (
        f"stigcompliance: PASS_MIN_DAYS in /etc/login.defs is "
        f"{config['PASS_MIN_DAYS']!r}, expected '1'"
    )


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-login-defs-pass-max-days"])
@pytest.mark.feature(
    "disaSTIGmedium", reason="PASS_MAX_DAYS is set to 60 by disaSTIGmedium"
)
def test_login_defs_pass_max_days_is_60(parse_file) -> None:
    config = parse_file.parse("/etc/login.defs", format="spacedelim")
    assert config["PASS_MAX_DAYS"] == "60", (
        f"stigcompliance: PASS_MAX_DAYS in /etc/login.defs is "
        f"{config['PASS_MAX_DAYS']!r}, expected '60'"
    )
