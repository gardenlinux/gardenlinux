import pytest
from plugins.shell import ShellRunner
from plugins.dpkg import Dpkg
from plugins.module import Kernel_Module
import json
import os
from pathlib import Path

# Define variables for the IP address, NVMe device, and subsystem name
IP_ADDRESS="127.0.0.1"
NVME_DEVICE="/tmp/nvme.img"
SUBSYSTEM_NAME="testnqn"
PORT_NUMBER="4420"
TRTYPE="tcp"
ADRFAM="ipv4"

REQUIRED_NVME_MODULE = [
            {"nvme_module": "nvme_tcp", "status": None},
            {"nvme_module": "nvmet_tcp", "status": None},
            {"nvme_module": "nvmet", "status": None},
            ]
#This fixture executes NVME configuration, yield to complete the test and then do bring back real system state after test
@pytest.fixture
def nvme_device(shell: ShellRunner, dpkg: Dpkg, kernel_module: Kernel_Module):
    mount_package_installed = False
    shell(f"truncate -s 512M {NVME_DEVICE}")
    if not dpkg.package_is_installed("mount"):
        mount_package_installed = True;
        shell("DEBIAN_FRONTEND=noninteractive apt-get install -y mount")
    shell(f"losetup -fP {NVME_DEVICE}")

    for entry in REQUIRED_NVME_MODULE:
        mod_name = entry["nvme_module"]
        if not kernel_module.is_module_loaded(mod_name):
            kernel_module.load_module(mod_name)
            entry["status"] = "Loaded"
    port = 1
    while os.path.exists(os.path.join("/sys/kernel/config/nvmet/ports", str(port))):
        port += 1
    # Create the NVMe subsystem directory
    os.makedirs(f"/sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}")

    # Set the subsystem to accept any host
    Path(f"/sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/attr_allow_any_host").write_text("1")

    # Create and configure the namespace
    os.makedirs(f"/sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/namespaces/{port}")

    Path(f"/sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/namespaces/{port}/device_path").write_text(NVME_DEVICE)
    Path(f"/sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/namespaces/{port}/enable").write_text("1")

    # Configure the NVMe-oF TCP port
    os.makedirs(f"/sys/kernel/config/nvmet/ports/{port}")
    Path(f"/sys/kernel/config/nvmet/ports/{port}/addr_traddr").write_text(IP_ADDRESS)
    Path(f"/sys/kernel/config/nvmet/ports/{port}/addr_trtype").write_text(TRTYPE)
    Path(f"/sys/kernel/config/nvmet/ports/{port}/addr_trsvcid").write_text(PORT_NUMBER)
    Path(f"/sys/kernel/config/nvmet/ports/{port}/addr_adrfam").write_text(ADRFAM)

    os.symlink(f"/sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}", f"/sys/kernel/config/nvmet/ports/{port}/subsystems/{SUBSYSTEM_NAME}")

    shell("nvme connect -t tcp -n testnqn -a 127.0.0.1 -s 4420")
    output = shell("nvme list -o json", capture_output=True)
    json_devices = json.loads(output.stdout)
    local_device = [device['DevicePath'] for device in json_devices['Devices'] if device["ModelNumber"] == "Linux"][0]
    shell(f"mkfs.ext4 {local_device}")
    os.makedirs("/mnt/nvme")
    shell(f"mount {local_device} /mnt/nvme")
    shell("echo 'foo' | tee /mnt/nvme/bar")

    yield local_device, "/mnt/nvme", "488"

    print("Teardown nvme device and clean up")
    shell("umount /mnt/nvme", ignore_exit_code=True)
    os.rmdir("/mnt/nvme")
    shell(f"nvme disconnect -n {SUBSYSTEM_NAME}", ignore_exit_code=True)
    os.remove(NVME_DEVICE)
    Path(f"/sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/namespaces/{port}/enable").write_text("0")
    Path(f"/sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/attr_allow_any_host").write_text("0")
    os.rmdir(f"/sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/namespaces/{port}")
    os.unlink(f"/sys/kernel/config/nvmet/ports/{port}/subsystems/{SUBSYSTEM_NAME}")
    os.rmdir(f"/sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}")
    os.rmdir(f"/sys/kernel/config/nvmet/ports/{port}")
    for entry in REQUIRED_NVME_MODULE:
        mod_name = entry["nvme_module"]
        if entry["status"] == "Loaded":
            kernel_module.unload_module(mod_name)
            entry["status"] = "None"
    if mount_package_installed == True:
        shell("DEBIAN_FRONTEND=noninteractive apt remove mount")
