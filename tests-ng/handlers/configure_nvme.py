import pytest
from plugins.shell import ShellRunner
from plugins.dpkg import Dpkg
from plugins.kernel_module import KernelModule
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

REQUIRED_NVME_MODULES = [
            {"name": "nvmet", "status": None},
            {"name": "nvmet_tcp", "status": None},
            {"name": "nvme_tcp", "status": None},
            ]
#This fixture executes NVME configuration, yield to complete the test and then do bring back real system state after test
@pytest.fixture
def nvme_device(shell: ShellRunner, dpkg: Dpkg, kernel_module: KernelModule):
    mount_package_installed = False
    shell(f"truncate -s 512M {NVME_DEVICE}")
    if not dpkg.package_is_installed("mount"):
        mount_package_installed = True;
        shell("DEBIAN_FRONTEND=noninteractive apt-get install -y mount")
    loop_device = shell(f"losetup -fP --show {NVME_DEVICE}", capture_output=True).stdout.strip()

    for entry in REQUIRED_NVME_MODULES:
        name = entry["name"]
        if not kernel_module.is_module_loaded(name):
            kernel_module.load_module(name)
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

    shell("nvme connect -t tcp -n testnqn -a 127.0.0.1 -s 4420", capture_output=True)
    output = shell("nvme list -o json", capture_output=True)
    json_devices = json.loads(output.stdout.strip())
    local_device = [device['DevicePath'] for device in json_devices['Devices'] if device["ModelNumber"] == "Linux"][0]
    mount_dir = "/tmp/nvme"
    shell(f"mkfs.ext4 -q {local_device}")
    os.makedirs(mount_dir)
    shell(f"mount {local_device} {mount_dir}")
    Path(f"{mount_dir}/bar").write_text("foo\n")

    yield local_device, mount_dir, "488"

    shell(f"umount {mount_dir}", ignore_exit_code=True)
    os.rmdir(mount_dir)
    shell(f"nvme disconnect -n {SUBSYSTEM_NAME}", capture_output=True, ignore_exit_code=True)
    Path(f"/sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/namespaces/{port}/enable").write_text("0")
    Path(f"/sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/attr_allow_any_host").write_text("0")
    os.rmdir(f"/sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/namespaces/{port}")
    os.unlink(f"/sys/kernel/config/nvmet/ports/{port}/subsystems/{SUBSYSTEM_NAME}")
    os.rmdir(f"/sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}")
    os.rmdir(f"/sys/kernel/config/nvmet/ports/{port}")
    os.remove(NVME_DEVICE)
    shell(f"losetup -d {loop_device}")
    # reorder the modules to unload in the reverse order of loading
    for entry in reversed(REQUIRED_NVME_MODULES):
        name = entry["name"]
        if entry["status"] == "Loaded":
            kernel_module.unload_module(name)
            entry["status"] = None
    if mount_package_installed == True:
        shell("DEBIAN_FRONTEND=noninteractive apt remove mount")
