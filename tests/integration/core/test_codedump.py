import pytest
from plugins.file import File
from plugins.shell import ShellRunner
from plugins.sysctl import Sysctl

# =============================================================================
# _prod Feature - Codedump
# =============================================================================


@pytest.mark.testcov(
    [
        "GL-TESTCOV-_prod-config-security-limits-disable-core-dumps",
    ]
)
@pytest.mark.feature("_prod")
def test_prod_security_limits_no_core_dumps(file: File):
    """Test that production has security limits disabling core dumps"""
    assert file.exists(
        "/etc/security/limits.conf"
    ), "Production should have core dump limits"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-_prod-config-security-limits-disable-core-dumps",
    ]
)
@pytest.mark.booted(reason="ulimit needs a booted system")
@pytest.mark.feature("_prod")
def test_prod_security_limits_no_core_dumps_check(shell: ShellRunner):
    """Test that production has security limits disabling core dumps"""
    result = shell("ulimit -Sc", capture_output=True)
    assert (
        result.stdout.strip() == "0"
    ), "Production should have core dump limits set to 0"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-_prod-config-sysctl-coredump-disable",
    ]
)
@pytest.mark.feature("_prod")
def test_prod_sysctl_coredump_disable(file: File):
    """Test that production has sysctl disabling core dumps"""
    assert file.exists(
        "/etc/sysctl.d/99-disable-core-dump.conf"
    ), "Production should have sysctl coredump disable"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-_prod-config-sysctl-coredump-disable",
    ]
)
@pytest.mark.feature("_prod")
@pytest.mark.booted(reason="sysctl needs a booted system")
def test_prod_sysctl_coredump_disable_check(sysctl: Sysctl):
    """Test that production has sysctl disabling core dumps"""
    assert (
        sysctl["fs.suid_dumpable"] == 0
    ), "Production should have sysctl coredump disable"
    assert (
        sysctl["kernel.core_pattern"] == "|/bin/false"
    ), "Production should have sysctl coredump pattern set to /bin/false"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-_prod-config-systemd-coredump-disable",
    ]
)
@pytest.mark.feature("_prod")
def test_prod_systemd_coredump_disable(file: File):
    """Test that production has systemd coredump configuration"""
    assert file.exists(
        "/etc/systemd/coredump.conf.d/disable_coredump.conf"
    ), "Production should have systemd coredump disable config"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-service-systemd-coredump-no-override",
    ]
)
@pytest.mark.feature("_prod")
def test_prod_no_systemd_coredump_service_override(file: File):
    """Test that production does not have systemd-coredump service override"""
    assert not file.exists(
        "/etc/systemd/system/systemd-coredump.service.d/override.conf"
    ), "Production should not have systemd-coredump service override"
