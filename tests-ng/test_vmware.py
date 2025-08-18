import pytest
import os
from plugins.file_content import file_content

file = [ "/etc/cloud/cloud.cfg" ] 
args = [ "ntp",
         "resizefs",
         "growpart",
        ]
vmware_files = [
        "/usr/bin/dscheck_VMwareGuestInfo",
        "/usr/lib/python3/dist-packages/cloudinit/sources/DataSourceVMwareGuestInfo.py",
        "/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg",
        "/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg",
        "/etc/cloud/cloud.cfg.d/99_enabled-datasources.cfg"
    ]

@pytest.mark.feature("vmware")
@pytest.mark.parametrize("filename", file)
@pytest.mark.parametrize("content", args)

def test_file_content(filename: str, content: str):
    if os.path.isfile(filename):
        if (file_content(filename, content)):
            assert False, f"Found {content} in {filename} which is not expected."
    else:
        assert False, "File does not exist"

@pytest.mark.parametrize("files_to_check", vmware_files)

def test_check_file(files_to_check: str):
    assert os.path.exists(files_to_check), (f"File {files_to_check} could not be found.")
