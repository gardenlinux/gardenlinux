import pytest
from plugins.file import File
from plugins.find import Find
from plugins.parse_file import ParseFile
from plugins.systemd import Systemd

# =============================================================================
# log Feature - Audit Rules Configuration
# =============================================================================


@pytest.mark.testcov(
    [
        "GL-TESTCOV-log-config-audit-permissions",
    ]
)
@pytest.mark.feature("log")
def test_log_audit_directory_permissions(find: Find, file: File):
    """Test that audit directory has correct permissions"""
    find.root_paths = "/etc/audit/rules.d"
    find.entry_type = "files"
    find.pattern = "*.rules"
    missing = [file_path for file_path in find if not file.has_mode(file_path, "0640")]
    assert (
        not missing
    ), f"Audit rules files should have permissions 0640, but these do not: {missing}"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-log-config-audit-rules-README",
        "GL-TESTCOV-log-config-audit-rules-base-config",
        "GL-TESTCOV-log-config-audit-rules-cont-fail",
        "GL-TESTCOV-log-config-audit-rules-ignore-error",
    ]
)
@pytest.mark.feature("log")
def test_log_audit_rules_files_exist(file: File):
    """Test that audit rules configuration files exist"""
    audit_rules = [
        "/etc/audit/rules.d/README",
        "/etc/audit/rules.d/10-base-config.rules",
        "/etc/audit/rules.d/12-cont-fail.rules",
        "/etc/audit/rules.d/12-ignore-error.rules",
    ]
    missing = [rule for rule in audit_rules if not file.exists(rule)]
    assert not missing, f"Missing audit rules files: {', '.join(missing)}"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-log-config-audit-rules-base-config",
    ]
)
@pytest.mark.feature("log")
def test_log_audit_rule_base_config_content(parse_file: ParseFile):
    """Test that audit rules configuration files contain the correct content"""
    lines = parse_file.lines("/etc/audit/rules.d/10-base-config.rules")
    assert lines == [
        "-D",
        "-b 8192",
        "--backlog_wait_time 60000",
        "-f 1",
    ], "Audit rules base configuration should contain the correct content"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-log-config-audit-rules-cont-fail",
    ]
)
@pytest.mark.feature("log")
def test_log_audit_rule_cont_fail_content(parse_file: ParseFile):
    """Test that audit rules configuration files contain the correct content"""
    lines = parse_file.lines("/etc/audit/rules.d/12-cont-fail.rules")
    assert lines == [
        "-c",
    ], "Audit rules cont fail configuration should contain the correct content"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-log-config-audit-rules-ignore-error",
    ]
)
@pytest.mark.feature("log")
def test_log_audit_rule_ignore_error_content(parse_file: ParseFile):
    """Test that audit rules configuration files contain the correct content"""
    lines = parse_file.lines("/etc/audit/rules.d/12-ignore-error.rules")
    assert lines == [
        "-i",
    ], "Audit rules ignore error configuration should contain the correct content"


# =============================================================================
# log Feature - Journald Configuration
# =============================================================================


@pytest.mark.testcov(
    [
        "GL-TESTCOV-log-config-journald-minimum",
    ]
)
@pytest.mark.feature("log")
def test_log_journald_minimum_config_exists(file: File):
    """Test that journald minimum configuration exists"""
    assert file.exists(
        "/etc/systemd/journald.conf.d/10-minimum.conf"
    ), "Journald minimum configuration should exist"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-log-config-journald-minimum",
    ]
)
@pytest.mark.feature("log")
def test_log_journald_minimum_config_content(parse_file: ParseFile):
    """Test that journald minimum configuration contains the correct content"""
    lines = parse_file.lines("/etc/systemd/journald.conf.d/10-minimum.conf")
    assert lines == [
        "[Journal]",
        "Seal=yes",
        "ReadKMsg=yes",
        "Audit=yes",
    ], "Journald minimum configuration should contain the correct content"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-log-config-journald-rsyslog",
    ]
)
@pytest.mark.feature("log")
def test_log_journald_rsyslog_config_exists(file: File):
    """Test that journald rsyslog integration configuration exists"""
    assert file.exists(
        "/etc/systemd/journald.conf.d/20-rsyslog.conf"
    ), "Journald rsyslog configuration should exist"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-log-config-journald-rsyslog",
    ]
)
@pytest.mark.feature("log")
def test_log_journald_rsyslog_config_content(parse_file: ParseFile):
    """Test that journald rsyslog integration configuration contains the correct content"""
    lines = parse_file.lines("/etc/systemd/journald.conf.d/20-rsyslog.conf")
    assert lines == [
        "[Journal]",
        "ForwardToSyslog=yes",
        "MaxLevelSyslog=info",
    ], "Journald rsyslog integration configuration should contain the correct content"


# =============================================================================
# log Feature - Rsyslog Configuration
# =============================================================================


@pytest.mark.testcov(
    [
        "GL-TESTCOV-log-config-rsyslog-conf",
    ]
)
@pytest.mark.feature("log")
def test_log_rsyslog_main_config_exists(file: File):
    """Test that main rsyslog configuration exists"""
    assert file.is_regular_file(
        "/etc/rsyslog.conf"
    ), "Main rsyslog configuration should exist"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-log-config-rsyslog-conf",
    ]
)
@pytest.mark.feature("log")
def test_log_rsyslog_main_config_content(parse_file: ParseFile):
    """Test that main rsyslog configuration contains the correct content"""
    lines = parse_file.lines("/etc/rsyslog.conf")
    assert lines == [
        "$FileOwner root",
        "$FileGroup adm",
        "$FileCreateMode 0640",
        "$DirCreateMode 0755",
        "$Umask 0022",
        "$WorkDirectory /var/spool/rsyslog",
        "$IncludeConfig /etc/rsyslog.d/*.conf",
    ], "Main rsyslog configuration should contain the correct content"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-log-config-rsyslog-input-conf",
    ]
)
@pytest.mark.feature("log")
def test_log_rsyslog_input_configs_exist(file: File):
    """Test that rsyslog input configurations exist"""
    input_configs = [
        "/etc/rsyslog.d/20-input.conf",
    ]
    missing = [cfg for cfg in input_configs if not file.exists(cfg)]
    assert not missing, f"Missing rsyslog input configs: {', '.join(missing)}"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-log-config-rsyslog-input-conf",
    ]
)
@pytest.mark.feature("log")
def test_log_rsyslog_input_config_content(parse_file: ParseFile):
    """Test that rsyslog input configuration contains the correct content"""
    lines = parse_file.lines("/etc/rsyslog.d/20-input.conf")
    assert (
        'module(load="imuxsock")' in lines
    ), "Rsyslog input configuration should contain the correct content"


# =============================================================================
# log Feature Services
# =============================================================================


@pytest.mark.testcov(
    ["GL-TESTCOV-log-service-auditd-enable", "GL-TESTCOV-ssh-service-auditd-enable"]
)
@pytest.mark.feature("log or ssh")
@pytest.mark.booted(reason="Requires systemd")
def test_log_auditd_service_enabled(systemd: Systemd):
    """Test that auditd.service is enabled"""
    assert systemd.is_enabled("auditd.service")


@pytest.mark.testcov(
    ["GL-TESTCOV-log-service-auditd-enable", "GL-TESTCOV-ssh-service-auditd-enable"]
)
@pytest.mark.feature("log or ssh")
@pytest.mark.booted(reason="Requires systemd")
def test_log_auditd_service_active(systemd: Systemd):
    """Test that auditd.service is active"""
    assert systemd.is_active("auditd.service")


@pytest.mark.testcov(["GL-TESTCOV-log-service-rsyslog-preset-disable"])
@pytest.mark.feature("log")
@pytest.mark.booted(reason="Requires systemd")
def test_log_rsyslog_service_disabled(systemd: Systemd):
    """Test that rsyslog.service is disabled by preset"""
    assert systemd.is_disabled("rsyslog.service")


@pytest.mark.testcov(["GL-TESTCOV-log-service-rsyslog-preset-disable"])
@pytest.mark.feature("log")
@pytest.mark.booted(reason="Requires systemd")
def test_log_rsyslog_service_inactive(systemd: Systemd):
    """Test that rsyslog.service is inactive"""
    assert systemd.is_inactive("rsyslog.service")


@pytest.mark.testcov(["GL-TESTCOV-log-service-systemd-journald-audit-socket-enable"])
@pytest.mark.feature("log")
@pytest.mark.booted(reason="Requires systemd")
def test_log_systemd_journald_audit_socket_service_enabled(systemd: Systemd):
    """Test that systemd-journald-audit.socket is enabled"""
    assert systemd.is_enabled("systemd-journald-audit.socket")


@pytest.mark.testcov(["GL-TESTCOV-log-service-systemd-journald-audit-socket-enable"])
@pytest.mark.feature("log")
@pytest.mark.booted(reason="Requires systemd")
def test_log_systemd_journald_audit_socket_service_active(systemd: Systemd):
    """Test that systemd-journald-audit.socket is active"""
    assert systemd.is_active("systemd-journald-audit.socket")
