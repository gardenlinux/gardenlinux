import pytest
from plugins.file import File
from plugins.parse_file import ParseFile
from plugins.systemd import Systemd

# =============================================================================
# azure Feature - Microsoft Azure
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-azure-config-network-unmanaged-devices"])
@pytest.mark.feature("azure")
def test_azure_networkd_unmanaged_devices_exists(file: File):
    """Test that Azure networkd unmanaged devices config exists"""
    assert file.exists("/etc/systemd/99-azure-unmanaged-devices.network")


@pytest.mark.setting_ids(["GL-SET-azure-config-network-unmanaged-devices"])
@pytest.mark.feature("azure")
def test_azure_networkd_unmanaged_devices_content(parse_file: ParseFile):
    """Test that Azure networkd unmanaged devices config content exists"""
    lines = parse_file.parse(
        "/etc/systemd/99-azure-unmanaged-devices.network", format="ini"
    )

    assert lines["Match"]["Driver"] == "mlx4_en mlx5_en mlx4_core mlx5_core"
    assert lines["Link"]["Unmanaged"] == "yes"


@pytest.mark.setting_ids(
    [
        "GL-SET-azure-config-udev-rules-azure-product-uuid",
        "GL-SET-azure-config-udev-rules-azure-storage",
    ]
)
@pytest.mark.feature("azure")
def test_azure_udev_rules_exist(file: File):
    """Test that Azure udev rules exist"""
    rules = [
        "/etc/udev/rules.d/66-azure-storage.rules",
        "/etc/udev/rules.d/99-azure-product-uuid.rules",
    ]
    missing = [rule for rule in rules if not file.exists(rule)]
    assert not missing, f"Missing Azure udev rules: {', '.join(missing)}"


# =============================================================================
# gcp Feature - Google Cloud Platform
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-gcp-config-instance-configs-run-dir"])
@pytest.mark.feature("gcp")
def test_gcp_instance_configs_run_dir_set(parse_file: ParseFile):
    """Test that GCP instance configs run directory is set"""
    contents = parse_file.parse("/etc/default/instance_configs.cfg", format="ini")
    assert contents["MetadataScripts"]["run_dir"] == "/var/tmp"


# =============================================================================
# gcp or gdch Feature - Google Cloud Platform or Google Distributed Cloud Hosted
# =============================================================================

# TODO: Disabled until https://github.com/gardenlinux/gardenlinux/issues/4335 is fixed.
# @pytest.mark.setting_ids(
#     [
#         "GL-SET-gcp-config-ssh-sshd-config-google-oslogin",
#         "GL-SET-gdch-config-ssh-sshd-config-google-oslogin",
#     ]
# )
# @pytest.mark.feature("gcp or gdch")
# def test_gcp_ssh_google_oslogin_config(parse_file: ParseFile):
#     """Test that GCP has Google OS Login SSH configuration"""
#     lines = parse_file.lines("/etc/ssh/sshd_config")
#     assert (
#         "AuthorizedKeysCommand /usr/libexec/google_authorized_keys" in lines
#     ), "GCP Google OS Login SSH configuration should contain AuthorizedKeysCommand /usr/libexec/google_authorized_keys"
#     assert (
#         "AuthorizedKeysCommandUser root" in lines
#     ), "GCP Google OS Login SSH configuration should contain AuthorizedKeysCommandUser root"


@pytest.mark.setting_ids(
    [
        "GL-SET-gcp-config-timezone-utc",
        "GL-SET-gdch-config-timezone-utc",
    ]
)
@pytest.mark.feature("gcp or gdch")
def test_gcp_or_gdch_timezone_utc(file: File):
    """Test that GCP or GDCH has UTC timezone configured"""
    assert file.is_symlink(
        "/usr/share/zoneinfo/localtime", "/etc/localtime"
    ), "GCP or GDCH timezone should be set to UTC"


@pytest.mark.setting_ids(
    [
        "GL-SET-gcp-config-udev-rules-gce-disk-removal",
    ]
)
@pytest.mark.feature("gcp")
def test_gcp_udev_gce_disk_removal_rules(file: File):
    """Test that GCP has GCE disk removal udev rules"""
    assert file.exists(
        "/etc/udev/rules.d/64-gce-disk-removal.rules"
    ), "GCP GCE disk removal udev rules should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-gcp-service-google-guest-agent-manager-mask",
    ]
)
@pytest.mark.feature("gcp")
def test_gcp_google_guest_agent_manager_masked(systemd: Systemd):
    """Test that GCP Google guest agent manager is masked"""
    assert systemd.is_masked(
        "google-guest-agent-manager.service"
    ), "GCP Google guest agent manager should be masked"


# =============================================================================
# cloud Feature - Generic Cloud Configuration
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-cloud-config-kernel-postinst-cmdline",
        "GL-SET-cloud-config-kernel-postinst-update-syslinux",
    ]
)
@pytest.mark.feature("cloud")
def test_cloud_kernel_postinst_scripts_exist(file: File):
    """Test that cloud kernel postinst scripts exist"""
    scripts = [
        "/etc/kernel/postinst.d/00-kernel-cmdline",
        "/etc/kernel/postinst.d/zz-update-syslinux",
    ]
    missing = [script for script in scripts if not file.exists(script)]
    assert not missing, f"Missing cloud kernel postinst scripts: {', '.join(missing)}"


@pytest.mark.setting_ids(["GL-SET-cloud-config-kernel-postrm-update-syslinux"])
@pytest.mark.feature("cloud")
def test_cloud_kernel_postrm_script_exists(file: File):
    """Test that cloud kernel postrm script exists"""
    assert file.exists("/etc/kernel/postrm.d/zz-update-syslinux")


@pytest.mark.setting_ids(["GL-SET-cloud-config-repart-root"])
@pytest.mark.feature("cloud")
def test_cloud_repart_root_config_exists(file: File):
    """Test that cloud repart root configuration exists"""
    assert file.is_regular_file("/etc/repart.d/root.conf")


@pytest.mark.setting_ids(["GL-SET-cloud-config-systemd-rngd-architecture"])
@pytest.mark.feature("cloud")
def test_cloud_rngd_architecture_config_exists(file: File):
    """Test that cloud rngd architecture configuration exists"""
    assert file.exists("/etc/systemd/system/rngd.service.d/architecture.conf")
