import fileinput
import os
import shutil

import pytest


@pytest.fixture
def sudoers_edit():
    for line in fileinput.input("/etc/sudoers", inplace=True, backup=".bak"):
        if not line.startswith("%sudo"):
            print(line, end="")
    yield
    shutil.copy2("/etc/sudoers.bak", "/etc/sudoers")
    os.remove("/etc/sudoers.bak")


# @pytest.mark.feature("not lima")
@pytest.mark.booted(reason="audit rule validation requires running audit subsystem")
@pytest.mark.root(reason="required to query audit logs")
def test_audit_rules_for_logging_attempts_to_delete_privileges(audit_rule):
    """
    As per DISA STIG requirement, we need to verify that the operating system
    generates audit records when successful/unsuccessful attempts to delete privileges occur

    Ref: SRG-OS-000466-GPOS-00210
    """
    for file in ["passwd", "shadow", "group", "sudoers", "sudoers.d", "pam.d"]:
        assert audit_rule(
            fs_watch_path=f"/etc/{file}", access_types="wa"
        ), f"stigcompliance: writing to or changing metadata of /etc/{file} should be audited"


@pytest.mark.skip("not implemented")
# @pytest.mark.feature("not lima")
@pytest.mark.booted(reason="audit rule validation requires running audit subsystem")
@pytest.mark.root(reason="required to query audit logs")
def test_audit_rules_for_files_capabilities_removal(audit_rule):
    """
    As per DISA STIG requirement, we need to verify that the operating system
    generates audit records when successful/unsuccessful attempts to delete privileges occur

    Ref: SRG-OS-000466-GPOS-00210
    """
    assert audit_rule(
        syscall="setcap"
    ), "stigcompliance: setcap syscall audit rule is not configured"


@pytest.mark.feature("_selinux")
@pytest.mark.booted(reason="audit rule validation requires running audit subsystem")
def test_audit_rules_for_selinux_policies_changes(audit_rule):
    """
    As per DISA STIG requirement, we need to verify that the operating system
    generates audit records when successful/unsuccessful attempts to delete privileges occur

    Ref: SRG-OS-000466-GPOS-00210
    """
    assert audit_rule(
        fs_watch_path="/etc/selinux", access_types="wa"
    ), "stigcompliance: changes of selinux configuration files should be audited"


# @pytest.mark.feature("not lima")
@pytest.mark.booted(reason="audit rule validation requires running audit subsystem")
@pytest.mark.root(reason="required to query audit logs")
def test_audit_rules_for_logging_attempts_to_modify_apparmor_policies(audit_rule):
    """
    As per DISA STIG requirement, we need to verify that the operating system
    generates audit records when successful/unsuccessful attempts to delete privileges occur

    Ref: SRG-OS-000466-GPOS-00210
    """
    for file in ["apparmor", "apparmor.d"]:
        assert audit_rule(
            fs_watch_path=f"/etc/{file}", access_types="wa"
        ), f"stigcompliance: writing to or changing metadata of /etc/{file} should be audited"


# @pytest.mark.feature("not lima")
@pytest.mark.booted(reason="audit rule validation requires running audit subsystem")
@pytest.mark.root(reason="required to query audit logs")
def test_attempt_to_delete_privileges_event_logged(audit_rule, shell, sudoers_edit):
    """
    As per DISA STIG requirement, we need to verify that the operating system
    generates audit records when successful/unsuccessful attempts to delete privileges occur

    Ref: SRG-OS-000466-GPOS-00210
    """

    result = shell(
        cmd="ausearch -f /etc/sudoers --just-one",
        capture_output=True,
    )

    assert (
        "<no matches>" not in result.stdout.strip()
    ), "stigcompliance: privileges deletion attempt is not detected"
