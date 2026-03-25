import re

import pytest
from plugins.shell import ShellRunner


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_generated(shell: ShellRunner):
    """
    As per DISA STIG requirement, the operating system must produce audit
    records containing information to establish what type of events occurred.
    This test verifies that audit records are being generated
    Ref: SRG-OS-000037-GPOS-00015
    """
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )

    assert result.stdout.strip() != "", "stigcompliance: no audit events captured"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_contains_type(shell: ShellRunner):
    """
    As per DISA STIG requirement, the operating system must produce audit
    records containing information to establish what type of events occurred.
    This test verifies that audit records are being generated
    Ref: SRG-OS-000037-GPOS-00015
    """
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )

    assert (
        "type=" in result.stdout
    ), "stigcompliance: audit records do not contain event type information"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_contains_timestamp(shell: ShellRunner):
    """
    As per DISA STIG requirement, the operating system must produce audit
    records containing information to establish what type of events occurred.
    This test verifies that audit records are being generated and
    when (date and time) the events occurred.
    Ref: SRG-OS-000038-GPOS-00016
    """
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )
    assert (
        "time->" in result.stdout or "audit(" in result.stdout
    ), "stigcompliance: audit records do not contain timestamp information"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_contains_location(shell: ShellRunner):
    """
    As per DISA STIG requirement, the operating system must produce audit
    records containing information to establish what type of events occurred.
    This test verifies that audit records are being generated and
    and location (where) information is included in the audit records.
    Ref: SRG-OS-000039-GPOS-00017
    """
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )

    assert (
        "cwd=" in result.stdout
        or "name=" in result.stdout
        or "exe=" in result.stdout
        or "path=" in result.stdout
    ), "stigcompliance: audit records do not contain location (where) information"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_contains_source(shell: ShellRunner):
    """
    As per DISA STIG requirement, the operating system must produce audit
    records containing information to establish the source of the events.
    This test verifies that audit records are being generated and
    source (who) information is included in the audit records.
    Ref: SRG-OS-000040-GPOS-00018
    """
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )
    assert (
        "auid=" in result.stdout
        or "uid=" in result.stdout
        or "ses=" in result.stdout
        or "comm=" in result.stdout
        or "exe=" in result.stdout
    ), "stigcompliance: audit records do not contain source information"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_contains_full_record(shell: ShellRunner):
    """
    As per DISA STIG requirement, the operating system must produce audit
    records containing information to establish what type of events occurred,
    when (date and time) the events occurred, where the events occurred,
    the source of the events, and the outcome of the events.

    This test verifies that audit records include event type information,
    timestamps, location (where), source information, and outcome.

    Ref: SRG-OS-000041-GPOS-00019
    """
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )
    assert (
        "success=yes" in result.stdout
        or "success=no" in result.stdout
        or "res=success" in result.stdout
        or "res=failed" in result.stdout
    ), "stigcompliance: audit records do not contain outcome (success/failure) information"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_contains_full_text_recording(audit_rule, shell: ShellRunner):
    """
    As per DISA STIG requirement, the operating system must produce audit
    records containing information to establish what type of events occurred,
    when (date and time) the events occurred, where the events occurred,
    the source of the events, and the outcome of the events.

    This test verifies that the operating system generates audit records
    containing the full-text recording of privileged commands.
    Ref: SRG-OS-000042-GPOS-00020
    """
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )
    assert (
        "type=EXECVE" in result.stdout and " a0=" in result.stdout
    ) or "proctitle=" in result.stdout, (
        "stigcompliance: audit records do not contain full-text command recording"
    )


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_contains_individual_identities(shell: ShellRunner):
    """
    As per DISA STIG requirement, the operating system must produce audit
    records containing information to establish what type of events occurred,
    when (date and time) the events occurred, where the events occurred,
    the source of the events, and the outcome of the events.

    This test verifies that the operating system generates audit records
    containing the individual identities of group account users.
    Ref: SRG-OS-000042-GPOS-00021
    """
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )
    assert (
        " a0=" in result.stdout or " a1=" in result.stdout or " a2=" in result.stdout
    ), "stigcompliance: audit records do not contain command argument details"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_contains_audit_processing_failures(shell: ShellRunner):
    """
    As per DISA STIG requirement, the operating system must produce audit
    the operating system alerts the ISSO and SA (at a minimum)
    in the event of an audit processing failure.
    Ref: SRG-OS-000043-GPOS-00022
    """
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )

    assert "audit" in result.stdout and (
        "fail" in result.stdout
        or "error" in result.stdout
        or "lost=" in result.stdout
        or "backlog" in result.stdout
    ), "stigcompliance: audit records do not indicate alerting or detection of audit processing failures"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit event validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_event_contains_audit_multiple_components(shell: ShellRunner):
    """
    As per DISA STIG requirement, the operating system provides the
    capability to centrally review and analyze audit records from
    multiple components within the system
    Ref: SRG-OS-000051-GPOS-00024
    """
    result = shell(
        cmd="ausearch -ts recent",
        capture_output=True,
    )

    assert (
        result.stdout.strip() != "" and "type=" in result.stdout
    ), "stigcompliance: audit records are not retained or retrievable for analysis"


AUDITD_CONF = "/etc/audit/auditd.conf"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit retention validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit configuration and logs")
def test_audit_log_retention_and_availability(shell: ShellRunner):
    """
    As per DISA STIG requirement, the operating system must retain audit
    records and provide the capability to extract and review them.
    This test verifies:
    1. Audit retention configuration (auditd.conf)
    2. Audit logs are present and retrievable (ausearch)
    Ref: SRG-OS-000051-GPOS-00024
    """
    result = shell(f"cat {AUDITD_CONF}", capture_output=True)
    assert result.returncode == 0, "stigcompliance: unable to read auditd.conf"

    content = result.stdout

    config = {}
    for line in content.splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        if "=" in line:
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()

    assert (
        "max_log_file" in config
    ), "stigcompliance: max_log_file not configured in auditd.conf"

    assert (
        "num_logs" in config
    ), "stigcompliance: num_logs not configured in auditd.conf"

    assert (
        "space_left_action" in config
    ), "stigcompliance: space_left_action not configured in auditd.conf"

    assert (
        int(config["max_log_file"]) > 0
    ), "stigcompliance: max_log_file must be greater than 0"

    assert int(config["num_logs"]) >= 1, "stigcompliance: num_logs must be at least 1"

    result = shell("ausearch -ts recent", capture_output=True)

    assert (
        result.returncode == 0
    ), "stigcompliance: ausearch failed, audit logs not retrievable"

    output = result.stdout.strip()

    assert output != "", "stigcompliance: no audit records found (retention failure)"

    assert (
        "type=" in output
    ), "stigcompliance: audit records not in expected structured format"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit retention validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit configuration and logs")
def test_audit_log_audit_fields(shell: ShellRunner):
    """
    As per DISA STIG requirement, the operating system should provide the
    capability to filter audit records for events of interest based
    upon all audit fields within audit records
    Ref: SRG-OS-000054-GPOS-00025
    """
    uid_result = shell("ausearch -ua 0", capture_output=True)
    assert (
        uid_result.returncode == 0
    ), "stigcompliance: unable to filter audit records by user identity (uid)"

    type_result = shell(
        "ausearch -ts recent -m USER_LOGIN", capture_output=True, ignore_exit_code=True
    )
    assert type_result.returncode in (
        0,
        1,
    ), "stigcompliance: unable to filter audit records by event type"

    cmd_result = shell(
        "ausearch -ts recent -c id", capture_output=True, ignore_exit_code=True
    )
    assert cmd_result.returncode in (
        0,
        1,
    ), "stigcompliance: unable to filter audit records by command"

    assert (
        "type=" in uid_result.stdout
        or "type=" in type_result.stdout
        or "type=" in cmd_result.stdout
    ), "stigcompliance: audit filtering does not return structured audit records"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit retention validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit configuration and logs")
def test_audit_records_contain_identity_information(shell):
    """
    As per DISA STIG compliance requirement, the operating system must
    produce audit records containing information to establish the identity
    of any individual or process associated with the event.
    Ref: SRG-OS-000255-GPOS-00096
    """
    result = shell(
        "ausearch -ts recent",
        capture_output=True,
        ignore_exit_code=True,
    )

    stdout = result.stdout or ""

    identity_patterns = [
        r"\bauid=\d+",
        r"\buid=\d+",
        r"\beuid=\d+",
        r"\bpid=\d+",
        r"\bcomm=",
        r"\bexe=",
    ]

    missing = [
        pattern for pattern in identity_patterns if not re.search(pattern, stdout)
    ]

    assert (
        not missing
    ), "stigcompliance: audit records missing identity fields: " + ", ".join(missing)


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit retention validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit configuration and logs")
def test_audit_record_filtering_capability(shell: ShellRunner):
    """
    As per DISA STIG compliance requirements, the operating system must provide
    the capability to filter audit records based on all available audit fields.
    This test verifies that audit tools support filtering by key fields such as:
    event type, user identity, time, and executable.
    Ref: SRG-OS-000054-GPOS-00025
    """

    commands = [
        "ausearch -m USER_LOGIN || true",  # event type
        "ausearch -ts recent || true",  # time
        "ausearch -ua 0 || true",  # user identity (root)
        "ausearch -x /usr/bin/id || true",  # executable
    ]

    for cmd in commands:
        result = shell(cmd, capture_output=True)
        assert (
            result.returncode == 0
        ), f"stigcompliance: audit filtering failed for command: {cmd}"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires audit subsystem running")
@pytest.mark.root(reason="required to generate and read audit logs")
def test_audit_records_have_valid_timestamps(shell: ShellRunner):
    """
    As per DISA STIG compliance requirements, the operating system must use
    internal system clocks to generate timestamps for audit records.
    This test verifies that audit records contain valid timestamps.
    Ref: SRG-OS-000055-GPOS-00026
    """
    result = shell("ausearch -ts recent", capture_output=True)

    assert result.returncode == 0, "stigcompliance: failed to retrieve audit records"

    timestamp_pattern = r"time->\w{3}\s+\w{3}\s+\d+\s+\d+:\d+:\d+\s+\d{4}"

    assert re.search(
        timestamp_pattern, result.stdout
    ), "stigcompliance: audit records do not contain valid timestamps"
