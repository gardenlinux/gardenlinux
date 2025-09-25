import pytest
import subprocess
from plugins.shell import ShellRunner
from handlers.configure_nvme import nvme_device
import os
import json
from pathlib import Path

module = [ 
    "nvme-tcp" 
    ]

@pytest.mark.booted
@pytest.mark.root
@pytest.mark.feature("nvme")
@pytest.mark.parametrize("module_name", module)
def test_kernel_module_availability(module_name, shell: ShellRunner):
    assert shell(f"modinfo {module_name}", 
        capture_output=True, ignore_exit_code=True), (
        f"Module not found {module_name}")

@pytest.mark.booted
@pytest.mark.root
@pytest.mark.modify
@pytest.mark.feature("nvme")
def test_nvme_locally(nvme_device, shell: ShellRunner):
    device, mount_point, size = nvme_device
    mount_info_line = shell(f"df -m | grep {mount_point}", capture_output=True)
    mount_info = [x.strip() for x in mount_info_line.stdout.split(" ") if x]
    assert mount_info[0] == device
    assert mount_info[1] == size
    assert Path("/mnt/nvme/bar").read_text().strip() == "foo", "NVME Test failed"
