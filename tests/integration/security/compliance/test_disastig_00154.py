import pytest
from plugins.shell import ShellRunner


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires LSM subsystem")
@pytest.mark.root(reason="required to inspect execution control mechanisms")
def test_execution_control_lsm_present(lsm):
    """
    As per DISA STIG requirement, the operating system must prevent program
    execution in accordance with local policies regarding software program usage.
    This test verifies that a Linux Security Module (AppArmor or SELinux)
    capable of enforcing execution control is present.
    Ref: SRG-OS-000368-GPOS-00154
    """
    assert (
        "apparmor" in lsm or "selinux" in lsm
    ), f"stigcompliance: no execution control mechanism present (active LSMs: {lsm})"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires mounted filesystem inspection")
@pytest.mark.root(reason="required to verify execution restrictions")
def test_tmp_mounted_noexec(shell: ShellRunner):
    """
    As per DISA STIG requirement, the operating system must prevent program
    execution in accordance with local policies regarding software program usage.
    This test verifies that /tmp is mounted with noexec.
    Ref: SRG-OS-000368-GPOS-00154
    """
    result = shell(
        "findmnt --noheadings -o OPTIONS -T /tmp",
        capture_output=True,
        ignore_exit_code=True,
    )
    assert result.returncode == 0, "stigcompliance: /tmp is not a separate mountpoint"
    assert "noexec" in result.stdout, "stigcompliance: /tmp is not mounted with noexec"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires mounted filesystem inspection")
@pytest.mark.root(reason="required to verify execution restrictions")
def test_var_tmp_mounted_noexec(shell: ShellRunner):
    """
    As per DISA STIG requirement, the operating system must prevent program
    execution in accordance with local policies regarding software program usage.
    This test verifies that /var/tmp is mounted with noexec.
    Ref: SRG-OS-000368-GPOS-00154
    """
    result = shell(
        "findmnt --noheadings -o OPTIONS -T /var/tmp",
        capture_output=True,
        ignore_exit_code=True,
    )
    assert (
        result.returncode == 0
    ), "stigcompliance: /var/tmp is not a separate mountpoint"
    assert (
        "noexec" in result.stdout
    ), "stigcompliance: /var/tmp is not mounted with noexec"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires LSM subsystem")
@pytest.mark.root(reason="required to verify enforcement state")
def test_apparmor_enforcing(shell: ShellRunner, dpkg):
    """
    As per DISA STIG requirement, the operating system must prevent program
    execution in accordance with local policies regarding software program usage.
    This test verifies that AppArmor is enforcing execution policies when present.
    Ref: SRG-OS-000368-GPOS-00154
    """
    if not dpkg.package_is_installed("apparmor"):
        pytest.skip("AppArmor not installed")

    result = shell(
        "apparmor_status",
        capture_output=True,
        ignore_exit_code=True,
    )

    if result.returncode != 0:
        pytest.skip("apparmor_status not available")

    assert (
        "enforce" in result.stdout.lower()
    ), "stigcompliance: AppArmor not enforcing execution policies"
