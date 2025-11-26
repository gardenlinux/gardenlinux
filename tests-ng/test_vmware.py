import os

import pytest
from plugins.parse_file import ParseFile

forbidden_config_values = [
    ("/etc/cloud/cloud.cfg", r"^.*\-\sntp$"),
    ("/etc/cloud/cloud.cfg", r"^.*\-\sresizefs$"),
    ("/etc/cloud/cloud.cfg", r"^.*\-\sgrowpart$"),
]

vmware_required_files = [
    "/usr/bin/dscheck_VMwareGuestInfo",
    "/usr/lib/python3/dist-packages/cloudinit/sources/DataSourceVMwareGuestInfo.py",
    "/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg",
    "/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg",
    "/etc/cloud/cloud.cfg.d/99_enabled-datasources.cfg",
]


@pytest.mark.feature("vmware")
@pytest.mark.parametrize("filename,content", forbidden_config_values)
def test_config_for_forbidden_value(filename: str, content: str, parse_file: ParseFile):
    assert not parse_file.match_regex(filename, content)


@pytest.mark.feature("vmware")
@pytest.mark.parametrize("file_to_check", vmware_required_files)
def test_required_files_exist(file_to_check: str):
    assert os.path.exists(file_to_check), f"File {file_to_check} could not be found."
