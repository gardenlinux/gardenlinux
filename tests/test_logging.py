from re import A

import pytest
from plugins.file import File
from plugins.find import Find
from plugins.parse_file import ParseFile

# =============================================================================
# log Feature - Audit Rules Configuration
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-log-config-audit-permissions",
    ]
)
@pytest.mark.feature("log")
def test_log_audit_directory_permissions(find: Find, file: File):
    """Test that audit directory has correct permissions"""
    find.root_paths = "/etc/audit/ruled.d"
    find.entry_type = "files"
    missing = [file_path for file_path in find if not file.has_mode(file_path, "0640")]
    assert (
        not missing
    ), f"Audit rules files should have permissions 0640, but these do not: {missing}"


@pytest.mark.setting_ids(
    [
        "GL-SET-log-config-audit-rules-README",
        "GL-SET-log-config-audit-rules-base-config",
        "GL-SET-log-config-audit-rules-cont-fail",
        "GL-SET-log-config-audit-rules-ignore-error",
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


@pytest.mark.setting_ids(
    [
        "GL-SET-log-config-audit-rules-base-config",
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
    ], f"Audit rules base configuration should contain the correct content"


@pytest.mark.setting_ids(
    [
        "GL-SET-log-config-audit-rules-cont-fail",
    ]
)
@pytest.mark.feature("log")
def test_log_audit_rule_cont_fail_content(parse_file: ParseFile):
    """Test that audit rules configuration files contain the correct content"""
    lines = parse_file.lines("/etc/audit/rules.d/12-cont-fail.rules")
    assert lines == [
        "-c",
    ], f"Audit rules cont fail configuration should contain the correct content"


@pytest.mark.setting_ids(
    [
        "GL-SET-log-config-audit-rules-ignore-error",
    ]
)
@pytest.mark.feature("log")
def test_log_audit_rule_ignore_error_content(parse_file: ParseFile):
    """Test that audit rules configuration files contain the correct content"""
    lines = parse_file.lines("/etc/audit/rules.d/12-ignore-error.rules")
    assert lines == [
        "-i",
    ], f"Audit rules ignore error configuration should contain the correct content"


# =============================================================================
# log Feature - Journald Configuration
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-log-config-journald-minimum",
    ]
)
@pytest.mark.feature("log")
def test_log_journald_minimum_config_exists(file: File):
    """Test that journald minimum configuration exists"""
    assert file.exists(
        "/etc/systemd/journald.conf.d/10-minimum.conf"
    ), "Journald minimum configuration should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-log-config-journald-minimum",
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
    ], f"Journald minimum configuration should contain the correct content"


@pytest.mark.setting_ids(
    [
        "GL-SET-log-config-journald-rsyslog",
    ]
)
@pytest.mark.feature("log")
def test_log_journald_rsyslog_config_exists(file: File):
    """Test that journald rsyslog integration configuration exists"""
    assert file.exists(
        "/etc/systemd/journald.conf.d/20-rsyslog.conf"
    ), "Journald rsyslog configuration should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-log-config-journald-rsyslog",
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
    ], f"Journald rsyslog integration configuration should contain the correct content"


# =============================================================================
# log Feature - Rsyslog Configuration
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-log-config-rsyslog-conf",
    ]
)
@pytest.mark.feature("log")
def test_log_rsyslog_main_config_exists(file: File):
    """Test that main rsyslog configuration exists"""
    assert file.is_regular_file(
        "/etc/rsyslog.conf"
    ), "Main rsyslog configuration should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-log-config-rsyslog-conf",
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
    ], f"Main rsyslog configuration should contain the correct content"


@pytest.mark.setting_ids(
    [
        "GL-SET-log-config-rsyslog-audit-log-service",
    ]
)
@pytest.mark.feature("log")
def test_log_rsyslog_audit_log_config_exists(file: File):
    """Test that rsyslog audit log service configuration exists"""
    assert file.exists(
        "/etc/rsyslog.d/60-audit-log-service.conf.disabled"
    ), "Rsyslog audit log configuration should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-log-config-rsyslog-input-conf",
        "GL-SET-log-config-rsyslog-input-klog",
        "GL-SET-log-config-rsyslog-input-mark",
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


@pytest.mark.setting_ids(
    [
        "GL-SET-log-config-rsyslog-input-conf",
    ]
)
@pytest.mark.feature("log")
def test_log_rsyslog_input_config_content(parse_file: ParseFile):
    """Test that rsyslog input configuration contains the correct content"""
    lines = parse_file.lines("/etc/rsyslog.d/20-input.conf")
    assert lines == [
        'module(load="imuxsock")',
    ], f"Rsyslog input configuration should contain the correct content"
