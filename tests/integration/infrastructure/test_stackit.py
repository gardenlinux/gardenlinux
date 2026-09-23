import pytest
from plugins.file import File
from plugins.parse_file import ParseFile
from plugins.systemd import Systemd

# =============================================================================
# stackit Feature - Cloud Init Configuration
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-stackit-config-cloud-datasource-identify"])
@pytest.mark.feature("stackit")
def test_stackit_ds_identify_exists(file: File):
    """Test that STACKIT cloud-init datasource identification config exists"""
    assert file.is_regular_file("/etc/cloud/ds-identify.cfg")


@pytest.mark.testcov(["GL-TESTCOV-stackit-config-cloud-datasource-identify"])
@pytest.mark.feature("stackit")
def test_stackit_ds_identify_content(parse_file: ParseFile):
    """Test that STACKIT cloud-init datasource identification config is correct"""
    lines = parse_file.lines("/etc/cloud/ds-identify.cfg")
    assert "datasource: OpenStack" in lines
    assert "policy: enabled" in lines


@pytest.mark.testcov(["GL-TESTCOV-stackit-config-cloud-datasource"])
@pytest.mark.feature("stackit")
def test_stackit_datasource_config_exists(file: File):
    """Test that STACKIT cloud-init datasource list config exists"""
    assert file.is_regular_file("/etc/cloud/cloud.cfg.d/50-datasource.cfg")


@pytest.mark.testcov(["GL-TESTCOV-stackit-config-cloud-datasource"])
@pytest.mark.feature("stackit")
def test_stackit_datasource_config_content(parse_file: ParseFile):
    """Test that STACKIT cloud-init datasource list contains ConfigDrive"""
    lines = parse_file.lines("/etc/cloud/cloud.cfg.d/50-datasource.cfg")
    assert any("ConfigDrive" in line for line in lines)


@pytest.mark.testcov(["GL-TESTCOV-stackit-config-cloud-network-config-disable"])
@pytest.mark.feature("stackit")
def test_stackit_cloud_network_config_disabled(file: File):
    """Test that STACKIT cloud-init network config is disabled"""
    assert file.is_regular_file("/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg")


@pytest.mark.testcov(["GL-TESTCOV-stackit-config-cloud-network-config-disable"])
@pytest.mark.feature("stackit")
def test_stackit_cloud_network_config_disabled_content(parse_file: ParseFile):
    """Test that STACKIT cloud-init network config disable content is correct"""
    lines = parse_file.lines("/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg")
    assert "network: {config: disabled}" in lines


# =============================================================================
# stackit Feature - Cloud Init User Configuration
# =============================================================================


@pytest.mark.testcov(
    [
        "GL-TESTCOV-stackit-config-cloud-user-name",
        "GL-TESTCOV-stackit-config-cloud-user-shell",
        "GL-TESTCOV-stackit-config-cloud-user-lock-passwd",
        "GL-TESTCOV-stackit-config-cloud-user-sudo",
    ]
)
@pytest.mark.feature("stackit")
def test_stackit_cloud_default_user_config_exists(file: File):
    """Test that STACKIT cloud-init default user config exists"""
    assert file.is_regular_file("/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg")


# =============================================================================
# stackit Feature - Kernel cmdline
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-stackit-config-kernel-cmdline-console"])
@pytest.mark.feature("stackit")
def test_stackit_kernel_cmdline_console_config_exists(file: File):
    """Test that STACKIT kernel console cmdline config exists"""
    assert file.is_regular_file("/etc/kernel/cmdline.d/10-console.cfg")


@pytest.mark.testcov(["GL-TESTCOV-stackit-config-kernel-cmdline-console"])
@pytest.mark.feature("stackit")
def test_stackit_kernel_cmdline_console_config_content(parse_file: ParseFile):
    """Test that STACKIT kernel cmdline enables serial console"""
    lines = parse_file.lines("/etc/kernel/cmdline.d/10-console.cfg", comment_char=[])
    assert any("console=ttyS0" in line for line in lines)


# =============================================================================
# stackit Feature - Chrony / Time Sync (KVM PTP)
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-stackit-config-chrony"])
@pytest.mark.feature("stackit")
def test_stackit_chrony_config_exists(file: File):
    """Test that STACKIT chrony configuration exists"""
    assert file.is_regular_file("/etc/chrony/chrony.conf")


@pytest.mark.testcov(["GL-TESTCOV-stackit-config-chrony"])
@pytest.mark.feature("stackit")
def test_stackit_chrony_config_uses_ptp0(parse_file: ParseFile):
    """Test that STACKIT chrony uses KVM PTP hardware clock at /dev/ptp0"""
    lines = parse_file.lines("/etc/chrony/chrony.conf")
    assert any(
        "refclock PHC /dev/ptp0" in line for line in lines
    ), "chrony must use KVM PTP clock source /dev/ptp0"


@pytest.mark.testcov(["GL-TESTCOV-stackit-service-chrony-preset-disable"])
@pytest.mark.feature("stackit")
def test_stackit_chrony_preset_disable_exists(file: File):
    """Test that STACKIT chrony preset disable file exists"""
    assert file.is_regular_file("/etc/systemd/system-preset/00-chrony-disable.preset")


@pytest.mark.testcov(["GL-TESTCOV-stackit-service-chrony-preset-disable"])
@pytest.mark.feature("stackit")
@pytest.mark.booted(reason="Requires systemd")
def test_stackit_chrony_wait_service_disabled(systemd: Systemd):
    """Test that chrony-wait.service is disabled by preset on STACKIT"""
    assert systemd.is_disabled("chrony-wait.service")


@pytest.mark.testcov(["GL-TESTCOV-stackit-service-chrony-preset-disable"])
@pytest.mark.feature("stackit")
@pytest.mark.booted(reason="Requires systemd")
def test_stackit_chrony_restricted_service_disabled(systemd: Systemd):
    """Test that chronyd-restricted.service is disabled by preset on STACKIT"""
    assert systemd.is_disabled("chronyd-restricted.service")


# =============================================================================
# stackit Feature - systemd-timesyncd excluded
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-stackit-service-no-systemd-timesyncd"])
@pytest.mark.feature("stackit")
def test_stackit_no_timesyncd_override(file: File):
    """Test that STACKIT does not have systemd-timesyncd override (uses chrony instead)"""
    assert not file.exists(
        "/etc/systemd/system/systemd-timesyncd.service.d/override.conf"
    )


# =============================================================================
# stackit Feature - cloud-init service
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-stackit-service-cloud-init-local-enable"])
@pytest.mark.feature("stackit")
@pytest.mark.booted(reason="Requires systemd")
def test_stackit_cloud_init_local_enabled(systemd: Systemd):
    """Test that cloud-init-local.service is enabled on STACKIT"""
    assert systemd.is_enabled("cloud-init-local.service")


@pytest.mark.testcov(["GL-TESTCOV-stackit-service-chrony-enable"])
@pytest.mark.feature("stackit")
@pytest.mark.booted(reason="Requires systemd")
def test_stackit_chrony_enabled(systemd: Systemd):
    """Test that chrony.service is enabled on STACKIT"""
    assert systemd.is_enabled("chrony.service")
