import os

import pytest
from plugins.parse_file import ParseFile


# Tests for most platforms
@pytest.mark.feature(
    "ali or aws or azure or gdch or openstack or vmware",
    reason="Cloud-init is installed on most cloud platforms.",
)
def test_cloud_init_installed():
    assert os.path.exists("/etc/cloud/cloud.cfg"), "Cloud-init should be installed."


@pytest.mark.feature(
    "(gcp or kvm or metal or metal_pxe) and not (openstack and metal)",
    reason="Cloud-init is not installed on these platforms; openstack-metal also includes the metal feature.",
)
def test_cloud_init_not_installed():
    assert not os.path.exists(
        "/etc/cloud/cloud.cfg"
    ), "Cloud-init should not be installed."


@pytest.mark.feature(
    "ali or aws or azure or openstack or vmware",
    reason="Cloud-init is installed on most cloud platforms; gdch has minimal config",
)
def test_cloud_init_debian_cloud_defaults(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["apt_preserve_sources_list"] is True
    assert config["system_info"]["default_user"]["shell"] == "/bin/bash"
    assert config["system_info"]["default_user"]["lock_passwd"] is True
    assert config["system_info"]["default_user"]["sudo"] == ["ALL=(ALL) NOPASSWD:ALL"]


@pytest.mark.feature(
    "ali or aws or openstack or vmware",
    reason="Cloud-init is installed on most cloud platforms; azure uses a different default user; gdch has minimal config",
)
def test_cloud_init_debian_cloud_user(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["system_info"]["default_user"]["name"] == "admin"


@pytest.mark.feature(
    "aws or azure or openstack or vmware",
    reason="Cloud-init is installed on most cloud platforms; ali does not manage host file; gdch has minimal config",
)
def test_cloud_init_debian_cloud_manage_etc_hosts(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["manage_etc_hosts"] is True


# Tests for some platforms
@pytest.mark.feature("ali or aws or openstack or vmware")
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


# Alibaba Cloud
@pytest.mark.feature("ali")
def test_ali_debian_cloud_ignore_manage_etc_hosts(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg"
    config = parse_file.parse(file, format="yaml")
    assert "manage_etc_hosts" not in config


@pytest.mark.feature("ali")
def test_ali_disable_network_config(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["network"]["config"] == "disabled"


# AWS
@pytest.mark.feature("aws")
def test_aws_disable_network_config(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["network"]["config"] == "disabled"


# Azure
@pytest.mark.feature("azure")
def test_azure_debian_cloud_user(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["system_info"]["default_user"]["name"] == "azureuser"


# GDCH - Google Distributed Cloud Hosted
@pytest.mark.feature("gdch")
def test_gdch_ntp_settings(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/91-gdch-system.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["ntp"]["enabled"] is True
    assert config["ntp"]["ntp_client"] == "chrony"
    assert "ntp1.org.internal" in config["ntp"]["servers"]


# OpenStack
@pytest.mark.feature("openstack")
def test_openstack_datasource_list(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/50-datasource.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["datasource_list"] == ["ConfigDrive", "OpenStack", "Ec2"]


@pytest.mark.feature("openstack and cloud")
def test_openstack_disable_network_config(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["network"]["config"] == "disabled"


@pytest.mark.feature("openstack and metal")
def test_openstackbaremetal_network_config(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/65-network-config.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["system_info"]["network"]["renderers"] == ["netplan", "networkd"]


@pytest.mark.feature("openstack")
def test_openstack_ds_identify(parse_file: ParseFile):
    file = "/etc/cloud/ds-identify.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["datasource"] == "OpenStack"
    assert config["policy"] == "enabled"


# VMware
@pytest.mark.feature("vmware")
def test_vmware_disable_network_config(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["network"]["config"] == "disabled"


@pytest.mark.feature("vmware")
def test_vmware_enabled_datasources(parse_file: ParseFile):
    file = "/etc/cloud/cloud.cfg.d/99_enabled-datasources.cfg"
    config = parse_file.parse(file, format="yaml")
    assert config["datasource_list"] == ["VMwareGuestInfo", "OVF"]


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
