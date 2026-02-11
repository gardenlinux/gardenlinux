import pytest
from plugins.file import File
from plugins.parse_file import ParseFile

# =============================================================================
# azure Feature - Microsoft Azure
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-azure-config-network-unmanaged-devices"])
@pytest.mark.feature("azure")
def test_azure_networkd_unmanaged_devices_exists(file: File):
    """Test that Azure networkd unmanaged devices config exists"""
    assert file.exists("/etc/systemd/network/99-unmanaged.network")


@pytest.mark.setting_ids(["GL-SET-azure-config-network-unmanaged-devices"])
@pytest.mark.feature("azure")
def test_azure_networkd_unmanaged_devices_content(parse_file: ParseFile):
    """Test that Azure networkd unmanaged devices config content exists"""
    lines = parse_file.lines("/etc/systemd/network/99-unmanaged.network")

    assert lines == [
        "[Match]",
        "Driver = mlx4_en mlx5_en mlx4_core mlx5_core",
        "[Link]",
        "Unmanaged = yes",
    ]


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
def test_gcp_instance_configs_run_dir_exists(file: File):
    """Test that GCP instance configs run directory exists"""
    assert file.exists("/run/google-instance-setup")


# =============================================================================
# cloud Feature - Generic Cloud Configuration
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-cloud-config-kernel-entry-token"])
@pytest.mark.feature("cloud")
def test_cloud_kernel_entry_token_exists(file: File):
    """Test that cloud kernel entry token configuration exists"""
    assert file.is_regular_file("/etc/kernel/entry-token")


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
