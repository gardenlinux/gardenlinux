import pytest
import os
from plugins.file_content import check_val_in_file

val_to_check = [ ("/etc/cloud/cloud.cfg", "ntp"),
             ("/etc/cloud/cloud.cfg", "resizefs"),
             ("/etc/cloud/cloud.cfg", "growpart") ] 

vmware_files = [
        "/usr/bin/dscheck_VMwareGuestInfo",
        "/usr/lib/python3/dist-packages/cloudinit/sources/DataSourceVMwareGuestInfo.py",
        "/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg",
        "/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg",
        "/etc/cloud/cloud.cfg.d/99_enabled-datasources.cfg"
    ]

@pytest.mark.feature("vmware")
@pytest.mark.parametrize("filename,content", val_to_check)

def test_file_content(filename: str, content: str):
    assert os.path.isfile(filename), "File does not exist"
    assert not check_val_in_file(filename, content), (
            f"Found {content} in {filename} which is not expected." )

@pytest.mark.parametrize("file_to_check", vmware_files)

def test_check_file(file_to_check: str):
    assert os.path.exists(file_to_check), (
            f"File {file_to_check} could not be found." )
