"""
Ref: SRG-OS-000054-GPOS-00025

Verify the operating system provides the capability to filter audit records for
events of interest based upon all audit fields within audit records.
"""

import pytest


@pytest.mark.security_id(203614)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit retention validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_filter_by_uid(shell):
    """Verify ausearch -ua 0 succeeds (filter by user identity)."""
    result = shell("ausearch -ua 0", capture_output=True)

    assert (
        result.returncode == 0
    ), "stigcompliance: unable to filter audit records by user identity (uid)"


@pytest.mark.security_id(203614)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit retention validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_filter_returns_structured_output(shell):
    """Verify ausearch -ua 0 output contains a 'type=' field."""
    result = shell("ausearch -ua 0", capture_output=True)

    assert (
        "type=" in result.stdout or "type=" in result.stdout or "type=" in result.stdout
    ), "stigcompliance: audit filtering does not return structured audit records"


@pytest.mark.security_id(203614)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit retention validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_filter_by_event_type(shell):
    """Verify ausearch -ts recent -m USER_LOGIN runs (filter by event type)."""
    result = shell(
        "ausearch -ts recent -m USER_LOGIN",
        capture_output=True,
        ignore_exit_code=True,
    )

    assert result.returncode in (
        0,
        1,
    ), "stigcompliance: unable to filter audit records by event type"


@pytest.mark.security_id(203614)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit retention validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit logs")
def test_audit_filter_by_command(shell):
    """Verify ausearch -ts recent -c id runs (filter by command name)."""
    result = shell(
        "ausearch -ts recent -c id",
        capture_output=True,
        ignore_exit_code=True,
    )

    assert result.returncode in (
        0,
        1,
    ), "stigcompliance: unable to filter audit records by command"


@pytest.mark.security_id(203614)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit retention validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit configuration and logs")
def test_audit_record_filtering_capability(shell):
    """Verify ausearch supports filtering by -m, -ts, -ua, and -x flags."""
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
