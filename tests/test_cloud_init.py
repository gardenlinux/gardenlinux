import os

import pytest
from plugins.parse_file import ParseFile
from plugins.systemd import Systemd

# =============================================================================
# Most Platforms Feature Cloud-init
# =============================================================================


@pytest.mark.feature(
    "ali or aws or azure or gdch or openstackbaremetal or openstack or vmware",
    reason="Cloud-init is installed on most cloud platforms.",
)
def test_cloud_init_installed():
    assert os.path.exists("/etc/cloud/cloud.cfg"), "Cloud-init should be installed."


@pytest.mark.feature(
    "(gcp or kvm or metal or metal_pxe) and not openstackbaremetal",
    reason="Cloud-init is not installed on these platforms; openstackbaremetal also includes the metal feature.",
)
def test_cloud_init_not_installed():
    assert not os.path.exists(
        "/etc/cloud/cloud.cfg"
    ), "Cloud-init should not be installed."


@pytest.mark.setting_ids(
    [
        "GL-SET-ali-config-cloud-user-shell",
        "GL-SET-ali-config-cloud-user-lock-passwd",
        "GL-SET-ali-config-cloud-user-sudo",
        "GL-SET-ali-config-cloud-apt-sources",
        "GL-SET-aws-config-cloud-user-shell",
        "GL-SET-aws-config-cloud-user-lock-passwd",
        "GL-SET-aws-config-cloud-user-sudo",
        "GL-SET-aws-config-cloud-apt-sources",
        "GL-SET-azure-config-cloud-user-shell",
        "GL-SET-azure-config-cloud-user-lock-passwd",
        "GL-SET-azure-config-cloud-user-sudo",
        "GL-SET-azure-config-cloud-apt-sources",
        "GL-SET-openstack-config-cloud-user-shell",
        "GL-SET-openstack-config-cloud-user-lock-passwd",
        "GL-SET-openstack-config-cloud-user-sudo",
        "GL-SET-openstack-config-cloud-apt-sources",
        "GL-SET-openstackbaremetal-config-cloud-user-shell",
        "GL-SET-openstackbaremetal-config-cloud-user-lock-passwd",
        "GL-SET-openstackbaremetal-config-cloud-user-sudo",
        "GL-SET-openstackbaremetal-config-cloud-apt-sources",
        "GL-SET-vmware-config-cloud-user-shell",
        "GL-SET-vmware-config-cloud-user-lock-passwd",
        "GL-SET-vmware-config-cloud-user-sudo",
        "GL-SET-vmware-config-cloud-apt-sources",
    ]
)
@pytest.mark.feature(
    "ali or aws or azure or openstackbaremetal or openstack or vmware",
    reason="Cloud-init is installed on most cloud platforms; gdch has minimal config",
)
def test_cloud_init_debian_cloud_defaults(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["apt_preserve_sources_list"] is True
    assert config["system_info"]["default_user"]["shell"] == "/bin/bash"
    assert config["system_info"]["default_user"]["lock_passwd"] is True
    assert config["system_info"]["default_user"]["sudo"] == ["ALL=(ALL) NOPASSWD:ALL"]


@pytest.mark.setting_ids(
    [
        "GL-SET-ali-config-cloud-user-name",
        "GL-SET-aws-config-cloud-user-name" "GL-SET-openstack-config-cloud-user-name",
        "GL-SET-openstackbaremetal-config-cloud-user-name",
        "GL-SET-vmware-config-cloud-user-name",
    ]
)
@pytest.mark.feature(
    "ali or aws or openstackbaremetal or openstack or vmware",
    reason="Cloud-init is installed on most cloud platforms; azure uses a different default user; gdch has minimal config",
)
def test_cloud_init_debian_cloud_user(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["system_info"]["default_user"]["name"] == "admin"


@pytest.mark.setting_ids(
    [
        "GL-SET-aws-config-cloud-manage-hosts",
        "GL-SET-azure-config-cloud-manage-hosts",
        "GL-SET-openstack-config-cloud-manage-hosts",
        "GL-SET-openstackbaremetal-config-cloud-manage-hosts",
        "GL-SET-vmware-config-cloud-manage-hosts",
    ]
)
@pytest.mark.feature(
    "aws or azure or openstackbaremetal or openstack or vmware",
    reason="Cloud-init is installed on most cloud platforms; ali does not manage host file; gdch has minimal config",
)
def test_cloud_init_debian_cloud_manage_etc_hosts(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["manage_etc_hosts"] is True


# =============================================================================
# Some Platforms Feature Cloud-init
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-ali-config-cloud-no-ntp",
        "GL-SET-ali-config-cloud-no-resizefs",
        "GL-SET-ali-config-cloud-no-growpart",
        "GL-SET-aws-config-cloud-no-ntp",
        "GL-SET-aws-config-cloud-no-resizefs",
        "GL-SET-aws-config-cloud-no-growpart",
        "GL-SET-openstack-config-cloud-no-ntp",
        "GL-SET-openstack-config-cloud-no-resizefs",
        "GL-SET-openstack-config-cloud-no-growpart",
        "GL-SET-openstackbaremetal-config-cloud-no-ntp",
        "GL-SET-openstackbaremetal-config-cloud-no-resizefs",
        "GL-SET-openstackbaremetal-config-cloud-no-growpart",
        "GL-SET-vmware-config-cloud-no-ntp",
        "GL-SET-vmware-config-cloud-no-resizefs",
        "GL-SET-vmware-config-cloud-no-growpart",
    ]
)
@pytest.mark.feature("ali or aws or openstack or openstackbaremetal or vmware")
@pytest.mark.parametrize("module", ["ntp", "resizefs", "growpart"])
def test_cloud_cfg_excludes_modules(parse_file: ParseFile, module: str):
    file = "/etc/cloud/cloud.cfg"
    config = parse_file.parse(file, format="yaml")
    for list_path in [
        "cloud_init_modules",
        "cloud_config_modules",
        "cloud_final_modules",
    ]:
        # Navigate to the list using dictionary access
        parts = list_path.split(".")
        target_list = config
        for part in parts:
            target_list = target_list[part]
        assert (
            module not in target_list
        ), f"Value {module} found in list {list_path} in {file}, but should not be present."


# =============================================================================
# ali Feature Cloud-init
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-ali-config-cloud-apt-sources",
        "GL-SET-ali-config-cloud-user-name",
        "GL-SET-ali-config-cloud-user-shell",
        "GL-SET-ali-config-cloud-user-lock-passwd",
        "GL-SET-ali-config-cloud-user-sudo",
    ]
)
@pytest.mark.feature("ali")
def test_ali_debian_cloud_ignore_manage_etc_hosts(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg"
    config = parse_file.parse(file, format="yaml")
    assert "manage_etc_hosts" not in config


@pytest.mark.setting_ids(
    [
        "GL-SET-ali-config-cloud-network-config-disable",
    ]
)
@pytest.mark.feature("ali")
def test_ali_disable_network_config(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["network"]["config"] == "disabled"


@pytest.mark.setting_ids(["GL-SET-ali-service-cloud-init-local-enable"])
@pytest.mark.feature("ali")
@pytest.mark.booted(reason="Requires systemd")
def test_ali_cloud_init_local_service_enabled(systemd: Systemd):
    """Test that cloud-init-local.service is enabled"""
    assert systemd.is_enabled("cloud-init-local.service")


@pytest.mark.setting_ids(["GL-SET-ali-service-cloud-init-local-enable"])
@pytest.mark.feature("ali")
@pytest.mark.booted(reason="Requires systemd")
def test_ali_cloud_init_local_service_inactive(systemd: Systemd):
    """Test that cloud-init-local.service is inactive"""
    assert systemd.is_inactive("cloud-init-local.service")


# =============================================================================
# aws Feature Cloud-init
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-aws-config-cloud-network-config-disable"])
@pytest.mark.feature("aws")
def test_aws_disable_network_config(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["network"]["config"] == "disabled"


@pytest.mark.setting_ids(["GL-SET-aws-service-cloud-init-local-enable"])
@pytest.mark.feature("aws")
@pytest.mark.hypervisor("amazon", reason="Requires Amazon AWS infrastructure")
@pytest.mark.booted(reason="Requires systemd")
def test_aws_cloud_init_local_service_enabled(systemd: Systemd):
    """Test that cloud-init-local.service is enabled"""
    assert systemd.is_enabled("cloud-init-local.service")


@pytest.mark.setting_ids(["GL-SET-aws-service-cloud-init-local-enable"])
@pytest.mark.feature("aws")
@pytest.mark.booted(reason="Requires systemd")
def test_aws_cloud_init_local_service_inactive(systemd: Systemd):
    """Test that cloud-init-local.service is inactive"""
    assert systemd.is_inactive("cloud-init-local.service")


# =============================================================================
# azure Feature Cloud-init
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-azure-config-cloud-user-name",
    ]
)
@pytest.mark.feature("azure")
def test_azure_debian_cloud_user(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["system_info"]["default_user"]["name"] == "azureuser"


@pytest.mark.setting_ids(["GL-SET-azure-service-cloud-init-local-enable"])
@pytest.mark.feature("azure")
@pytest.mark.booted(reason="Requires systemd")
def test_azure_cloud_init_local_service_enabled(systemd: Systemd):
    """Test that cloud-init-local.service is enabled"""
    assert systemd.is_enabled("cloud-init-local.service")


@pytest.mark.setting_ids(["GL-SET-azure-service-cloud-init-local-enable"])
@pytest.mark.feature("azure")
@pytest.mark.booted(reason="Requires systemd")
def test_azure_cloud_init_local_service_inactive(systemd: Systemd):
    """Test that cloud-init-local.service is inactive"""
    assert systemd.is_inactive("cloud-init-local.service")


# =============================================================================
# gcp Feature Cloud-init
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-gcp-service-no-cloud-init-local"])
@pytest.mark.feature("gcp")
@pytest.mark.booted(reason="Requires systemd")
def test_gcp_no_cloud_init_local_service(systemd: Systemd):
    """Test that cloud-init.service is not installed"""
    assert not any(
        u.unit == "cloud-init-local.service" for u in systemd.list_installed_units()
    )


# =============================================================================
# gdch Feature Cloud-init
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-gdch-config-cloud-ntp",
    ]
)
@pytest.mark.feature("gdch")
def test_gdch_ntp_settings(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/91-gdch-system.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["ntp"]["enabled"] is True
    assert config["ntp"]["ntp_client"] == "chrony"
    assert "ntp1.org.internal" in config["ntp"]["servers"]


@pytest.mark.setting_ids(["GL-SET-gdch-service-cloud-init-local-enable"])
@pytest.mark.feature("gdch")
@pytest.mark.booted(reason="Requires systemd")
def test_gdch_cloud_init_local_service_enabled(systemd: Systemd):
    """Test that cloud-init-local.service is enabled"""
    assert systemd.is_enabled("cloud-init-local.service")


@pytest.mark.setting_ids(["GL-SET-gdch-service-cloud-init-local-enable"])
@pytest.mark.feature("gdch")
@pytest.mark.booted(reason="Requires systemd")
def test_gdch_cloud_init_local_service_inactive(systemd: Systemd):
    """Test that cloud-init-local.service is inactive"""
    assert systemd.is_inactive("cloud-init-local.service")


# =============================================================================
# lima Feature Cloud-init
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-lima-service-cloud-init-local-enable"])
@pytest.mark.feature("lima")
@pytest.mark.booted(reason="Requires systemd")
def test_lima_cloud_init_local_service_enabled(systemd: Systemd):
    """Test that cloud-init-local.service is enabled"""
    assert systemd.is_enabled("cloud-init-local.service")


@pytest.mark.setting_ids(["GL-SET-lima-service-cloud-init-local-enable"])
@pytest.mark.feature("lima")
@pytest.mark.booted(reason="Requires systemd")
def test_lima_cloud_init_local_service_inactive(systemd: Systemd):
    """Test that cloud-init-local.service is inactive"""
    assert systemd.is_inactive("cloud-init-local.service")


# =============================================================================
# openstack Feature Cloud-init
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-openstack-config-cloud-datasource",
        "GL-SET-openstackbaremetal-config-cloud-datasource",
    ]
)
@pytest.mark.feature("openstack or openstackbaremetal")
def test_openstack_datasource_list(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/50-datasource.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["datasource_list"] == ["ConfigDrive", "OpenStack", "Ec2"]


@pytest.mark.setting_ids(
    [
        "GL-SET-openstack-config-cloud-datasource-identify",
    ]
)
@pytest.mark.feature("openstack")
def test_openstack_ds_identify(parse_file: ParseFile):
    file = "/etc/cloud/ds-identify.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["datasource"] == "OpenStack"
    assert config["policy"] == "enabled"


@pytest.mark.setting_ids(
    [
        "GL-SET-openstack-config-cloud-network-config-disable",
    ]
)
@pytest.mark.feature("openstack")
def test_openstack_disable_network_config(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["network"]["config"] == "disabled"


@pytest.mark.setting_ids(["GL-SET-openstack-service-cloud-init-local-enable"])
@pytest.mark.feature("openstack")
@pytest.mark.booted(reason="Requires systemd")
def test_openstack_cloud_init_local_service_enabled(systemd: Systemd):
    """Test that cloud-init-local.service is enabled"""
    assert systemd.is_enabled("cloud-init-local.service")


@pytest.mark.setting_ids(["GL-SET-openstack-service-cloud-init-local-enable"])
@pytest.mark.feature("openstack")
@pytest.mark.booted(reason="Requires systemd")
def test_openstack_cloud_init_local_service_active(systemd: Systemd):
    """Test that cloud-init-local.service is active"""
    assert systemd.is_active("cloud-init-local.service")


# =============================================================================
# openstackbaremetal Feature Cloud-init
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-openstackbaremetal-config-cloud-network-config",
    ]
)
@pytest.mark.feature("openstackbaremetal")
def test_openstackbaremetal_network_config(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/65-network-config.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["system_info"]["network"]["renderers"] == ["netplan", "networkd"]


@pytest.mark.setting_ids(
    [
        "GL-SET-openstackbaremetal-config-cloud-datasource-identify",
    ]
)
@pytest.mark.feature("openstackbaremetal")
def test_openstackbaremetal_ds_identify(parse_file: ParseFile):
    file = "/etc/cloud/ds-identify.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["datasource"] == "OpenStack"
    assert config["policy"] == "enabled"


@pytest.mark.setting_ids(["GL-SET-openstackbaremetal-service-cloud-init-local-enable"])
@pytest.mark.feature("openstackbaremetal")
@pytest.mark.booted(reason="Requires systemd")
def test_openstackbaremetal_cloud_init_local_service_enabled(systemd: Systemd):
    """Test that cloud-init-local.service is enabled"""
    assert systemd.is_enabled("cloud-init-local.service")


@pytest.mark.setting_ids(["GL-SET-openstackbaremetal-service-cloud-init-local-enable"])
@pytest.mark.feature("openstackbaremetal")
@pytest.mark.booted(reason="Requires systemd")
def test_openstackbaremetal_cloud_init_local_service_active(systemd: Systemd):
    """Test that cloud-init-local.service is active"""
    assert systemd.is_active("cloud-init-local.service")


# =============================================================================
# vmware Feature Cloud-init
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-vmware-config-cloud-network-config-disable",
    ]
)
@pytest.mark.feature("vmware")
def test_vmware_disable_network_config(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["network"]["config"] == "disabled"


@pytest.mark.setting_ids(
    [
        "GL-SET-vmware-config-cloud-datasources",
    ]
)
@pytest.mark.feature("vmware")
def test_vmware_enabled_datasources(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/99_enabled-datasources.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["datasource_list"] == ["VMwareGuestInfo", "OVF"]


@pytest.mark.setting_ids(
    [
        "GL-SET-vmware-config-cloud-datasource-vmwareguestinfo",
        "GL-SET-vmware-config-cloud-datasource-identify",
    ]
)
@pytest.mark.feature("vmware")
@pytest.mark.parametrize(
    "file_path",
    [
        "/usr/lib/python3/dist-packages/cloudinit/sources/DataSourceVMwareGuestInfo.py",
        "/usr/bin/dscheck_VMwareGuestInfo",
    ],
)
def test_vmware_datasource_files_exist(file_path: str):
    assert os.path.exists(file_path), f"File {file_path} could not be found."


@pytest.mark.setting_ids(["GL-SET-vmware-service-cloud-init-local-enable"])
@pytest.mark.feature("vmware")
@pytest.mark.booted(reason="Requires systemd")
def test_vmware_cloud_init_local_service_enabled(systemd: Systemd):
    """Test that cloud-init-local.service is enabled"""
    assert systemd.is_enabled("cloud-init-local.service")


@pytest.mark.setting_ids(["GL-SET-vmware-service-cloud-init-local-enable"])
@pytest.mark.feature("vmware")
@pytest.mark.booted(reason="Requires systemd")
def test_vmware_cloud_init_local_service_inactive(systemd: Systemd):
    """Test that cloud-init-local.service is inactive"""
    assert systemd.is_inactive("cloud-init-local.service")
