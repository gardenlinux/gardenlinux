import os

import pytest
from plugins.parse_file import FileContent


# Tests for most platforms
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


@pytest.mark.feature(
    "ali or aws or azure or openstackbaremetal or openstack or vmware",
    reason="Cloud-init is installed on most cloud platforms; gdch has minimal config",
)
def test_cloud_init_debian_cloud_defaults(file_content: FileContent):
    file = "/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg"
    mapping = {
        "apt_preserve_sources_list": True,
        "system_info.default_user.shell": "/bin/bash",
        "system_info.default_user.lock_passwd": True,
        "system_info.default_user.sudo": ["ALL=(ALL) NOPASSWD:ALL"],
    }
    format = "yaml"
    result = file_content.get_mapping(
        file,
        mapping,
        format=format,
    )
    assert result is not None, f"Could not parse file: {file}"
    assert result.all_match, (
        f"Could not find expected mapping in {file} (format={format}) for {mapping}. "
        f"missing={result.missing}, wrong={{{result.wrong_formatted}}}"
    )


@pytest.mark.feature(
    "ali or aws or openstackbaremetal or openstack or vmware",
    reason="Cloud-init is installed on most cloud platforms; azure uses a different default user; gdch has minimal config",
)
def test_cloud_init_debian_cloud_user(file_content: FileContent):
    file = "/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg"
    mapping = {
        "system_info.default_user.name": "admin",
    }
    format = "yaml"
    result = file_content.get_mapping(
        file,
        mapping,
        format=format,
    )
    assert result is not None, f"Could not parse file: {file}"
    assert result.all_match, (
        f"Could not find expected mapping in {file} (format={format}) for {mapping}. "
        f"missing={result.missing}, wrong={{{result.wrong_formatted}}}"
    )


@pytest.mark.feature(
    "aws or azure or openstackbaremetal or openstack or vmware",
    reason="Cloud-init is installed on most cloud platforms; ali does not manage host file; gdch has minimal config",
)
def test_cloud_init_debian_cloud_manage_etc_hosts(file_content: FileContent):
    file = "/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg"
    mapping = {
        "manage_etc_hosts": True,
    }
    format = "yaml"
    result = file_content.get_mapping(
        file,
        mapping,
        format=format,
    )
    assert result is not None, f"Could not parse file: {file}"
    assert result.all_match, (
        f"Could not find expected mapping in {file} (format={format}) for {mapping}. "
        f"missing={result.missing}, wrong={{{result.wrong_formatted}}}"
    )


# Tests for some platforms
@pytest.mark.feature("ali or aws or openstack or openstackbaremetal or vmware")
@pytest.mark.parametrize("module", ["ntp", "resizefs", "growpart"])
def test_cloud_cfg_excludes_modules(file_content: FileContent, module: str):
    for list_path in [
        "cloud_init_modules",
        "cloud_config_modules",
        "cloud_final_modules",
    ]:
        file = "/etc/cloud/cloud.cfg"
        list_path = list_path
        value = module
        format = "yaml"
        found = file_content.check_list(
            file, list_path, value, format=format, invert=True
        )
        assert (
            found
        ), f"Value {value} found in list {list_path} in {file}, but should not be present."


# Alibaba Cloud
@pytest.mark.feature("ali")
def test_ali_debian_cloud_ignore_manage_etc_hosts(file_content: FileContent):
    file = "/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg"
    mapping = {
        "manage_etc_hosts": True,
    }
    format = "yaml"
    result = file_content.get_mapping(file, mapping, format=format)
    assert result is not None, f"Could not parse file: {file}"
    assert result.missing == ["manage_etc_hosts"], (
        f"Expected mapping in {file} (format={format}) for {mapping} to be missing, but it was present."
        f"missing={result.missing}, wrong={{{result.wrong_formatted}}}"
    )


@pytest.mark.feature("ali")
def test_ali_disable_network_config(file_content: FileContent):
    file = "/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg"
    mapping = {
        "network.config": "disabled",
    }
    format = "yaml"
    result = file_content.get_mapping(file, mapping, format=format)
    assert result is not None, f"Could not parse file: {file}"
    assert result.all_match, (
        f"Could not find expected mapping in {file} (format={format}) for {mapping}. "
        f"missing={result.missing}, wrong={{{result.wrong_formatted}}}"
    )


# AWS
@pytest.mark.feature("aws")
def test_aws_disable_network_config(file_content: FileContent):
    file = "/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg"
    mapping = {
        "network.config": "disabled",
    }
    format = "yaml"
    result = file_content.get_mapping(file, mapping, format=format)
    assert result is not None, f"Could not parse file: {file}"
    assert result.all_match, (
        f"Could not find expected mapping in {file} (format={format}) for {mapping}. "
        f"missing={result.missing}, wrong={{{result.wrong_formatted}}}"
    )


# Azure
@pytest.mark.feature("azure")
def test_azure_debian_cloud_user(file_content: FileContent):
    file = "/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg"
    mapping = {
        "system_info.default_user.name": "azureuser",
    }
    format = "yaml"
    result = file_content.get_mapping(file, mapping, format=format)
    assert result is not None, f"Could not parse file: {file}"
    assert result.all_match, (
        f"Could not find expected mapping in {file} (format={format}) for {mapping}. "
        f"missing={result.missing}, wrong={{{result.wrong_formatted}}}"
    )


# GDCH - Google Distributed Cloud Hosted
@pytest.mark.feature("gdch")
def test_gdch_ntp_settings(file_content: FileContent):
    file = "/etc/cloud/cloud.cfg.d/91-gdch-system.cfg"

    mapping = {
        "ntp.enabled": True,
        "ntp.ntp_client": "chrony",
    }
    format = "yaml"
    result = file_content.get_mapping(file, mapping, format=format)
    assert result is not None, f"Could not parse file: {file}"
    assert result.all_match, (
        f"Could not find expected mapping in {file} (format={format}) for {mapping}. "
        f"missing={result.missing}, wrong={{{result.wrong_formatted}}}"
    )

    list_path = "ntp.servers"
    value = "ntp1.org.internal"
    format = "yaml"
    found = file_content.check_list(file, list_path, value, format=format)
    assert (
        found
    ), f"Value {value} not found in list {list_path} in {file}, but should be present."


# OpenStack
@pytest.mark.feature("openstack or openstackbaremetal")
def test_openstack_datasource_list(file_content: FileContent):
    file = "/etc/cloud/cloud.cfg.d/50-datasource.cfg"
    mapping = {
        "datasource_list": ["ConfigDrive", "OpenStack", "Ec2"],
    }
    format = "yaml"
    result = file_content.get_mapping(file, mapping, format=format)
    assert result is not None, f"Could not parse file: {file}"
    assert result.all_match, (
        f"Could not find expected mapping in {file} (format={format}) for {mapping}. "
        f"missing={result.missing}, wrong={{{result.wrong_formatted}}}"
    )


@pytest.mark.feature("openstack")
def test_openstack_disable_network_config(file_content: FileContent):
    file = "/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg"
    mapping = {
        "network.config": "disabled",
    }
    format = "yaml"
    result = file_content.get_mapping(file, mapping, format=format)
    assert result is not None, f"Could not parse file: {file}"
    assert result.all_match, (
        f"Could not find expected mapping in {file} (format={format}) for {mapping}. "
        f"missing={result.missing}, wrong={{{result.wrong_formatted}}}"
    )


@pytest.mark.feature("openstackbaremetal")
def test_openstackbaremetal_network_config(file_content: FileContent):
    file = "/etc/cloud/cloud.cfg.d/65-network-config.cfg"
    mapping = {
        "system_info.network.renderers": ["netplan", "networkd"],
    }
    format = "yaml"
    result = file_content.get_mapping(file, mapping, format=format)
    assert result is not None, f"Could not parse file: {file}"
    assert result.all_match, (
        f"Could not find expected mapping in {file} (format={format}) for {mapping}. "
        f"missing={result.missing}, wrong={{{result.wrong_formatted}}}"
    )


@pytest.mark.feature("openstack or openstackbaremetal")
def test_openstack_ds_identify(file_content: FileContent):
    file = "/etc/cloud/ds-identify.cfg"
    mapping = {
        "datasource": "OpenStack",
        "policy": "enabled",
    }
    format = "yaml"
    result = file_content.get_mapping(file, mapping, format=format)
    assert result is not None, f"Could not parse file: {file}"
    assert result.all_match, (
        f"Could not find expected mapping in {file} (format={format}) for {mapping}. "
        f"missing={result.missing}, wrong={{{result.wrong_formatted}}}"
    )


# VMware
@pytest.mark.feature("vmware")
def test_vmware_disable_network_config(file_content: FileContent):
    file = "/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg"
    mapping = {
        "network.config": "disabled",
    }
    format = "yaml"
    result = file_content.get_mapping(file, mapping, format=format)
    assert result is not None, f"Could not parse file: {file}"
    assert result.all_match, (
        f"Could not find expected mapping in {file} (format={format}) for {mapping}. "
        f"missing={result.missing}, wrong={{{result.wrong_formatted}}}"
    )


@pytest.mark.feature("vmware")
def test_vmware_enabled_datasources(file_content: FileContent):
    file = "/etc/cloud/cloud.cfg.d/99_enabled-datasources.cfg"
    mapping = {
        "datasource_list": ["VMwareGuestInfo", "OVF"],
    }
    format = "yaml"
    result = file_content.get_mapping(file, mapping, format=format)
    assert result is not None, f"Could not parse file: {file}"
    assert result.all_match, (
        f"Could not find expected mapping in {file} (format={format}) for {mapping}. "
        f"missing={result.missing}, wrong={{{result.wrong_formatted}}}"
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
