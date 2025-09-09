import pytest
import subprocess
from plugins.shell import ShellRunner
<<<<<<< HEAD
from handlers.configure_nvme import nvme_device
=======
>>>>>>> c3b66280 (Port nvme test to new test framework)
import os
import json

module = [ 
    "nvme-tcp" 
    ]

<<<<<<< HEAD
=======
# Define variables for the IP address, NVMe device, and subsystem name
IP_ADDRESS="127.0.0.1"
NVME_DEVICE="/tmp/nvme.img"
SUBSYSTEM_NAME="testnqn"
PORT_NUMBER="4420"
TRTYPE="tcp"
ADRFAM="ipv4"

>>>>>>> c3b66280 (Port nvme test to new test framework)
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
<<<<<<< HEAD
@pytest.mark.modify
@pytest.mark.feature("nvme")
def test_nvme_locally(nvme_device, shell: ShellRunner):
    device, mount_point, size = nvme_device
    mount_info_line = shell(f"df -m | grep {mount_point}", capture_output=True, ignore_exit_code=False)
    mount_info = [x.strip() for x in mount_info_line.stdout.split(" ") if x]
    assert mount_info[0] == device
    assert mount_info[1] == size
    assert ((shell(f"cat /mnt/bar", capture_output=True, ignore_exit_code=False)).stdout.strip() == 'foo')
=======
@pytest.mark.feature("nvme")
def test_nvme_locally(shell: ShellRunner):
    configure_nvme_out = (shell("./helper/configure_nvme.sh connect", capture_output=True, ignore_exit_code=False)).stdout.strip() 
    device, mount_point, size = [x.strip().strip(',') for x in configure_nvme_out.split(",")]
    mount_info_line = shell(f"df -m | grep {mount_point}", capture_output=True, ignore_exit_code=False)
    mount_info = [x.strip() for x in mount_info_line.stdout.split(" ") if x]
    assert mount_info[0] == device, ("Nvme Mount Failed")
    assert mount_info[1] == size, ("Nvme Mount failed")
    assert ((shell(f"cat /mnt/bar", capture_output=True, ignore_exit_code=False)).stdout.strip() == 'foo')
<<<<<<< HEAD
    shell("./configure_nvme.sh disconnect", capture_output=True, ignore_exit_code=False)
>>>>>>> c3b66280 (Port nvme test to new test framework)
=======
    shell("./helper/configure_nvme.sh disconnect", capture_output=True, ignore_exit_code=False)
>>>>>>> ead5ef4f (Move configure script to helper folder)
