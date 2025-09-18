import pytest
from plugins.shell import ShellRunner
from plugins.dpkg import Dpkg
from plugins.module import Module
import json
import os

# Define variables for the IP address, NVMe device, and subsystem name
IP_ADDRESS="127.0.0.1"
NVME_DEVICE="/tmp/nvme.img"
SUBSYSTEM_NAME="testnqn"
PORT_NUMBER="4420"
TRTYPE="tcp"
ADRFAM="ipv4"

REQUIRED_NVME_MODULE = [
            {"nvme_module": "nvme_tcp", "status": None},
            {"nvme_module": "nvmet-tcp", "status": None},
            {"nvme_module": "nvmet", "status": None},
            ]
@pytest.fixture
def nvme_device(shell: ShellRunner, dpkg: Dpkg, module: Module):
    mount_package_installed = False
    shell(f"truncate -s 512M {NVME_DEVICE}")
    if not dpkg.package_is_installed("mount"):
        mount_package_installed = True;
        shell("DEBIAN_FRONTEND=noninteractive apt-get install -y mount")
    shell(f"losetup -fP {NVME_DEVICE}")

    for entry in REQUIRED_NVME_MODULE:
        mod_name = entry["nvme_module"]
        if not module.is_module_loaded(mod_name):
            module.load_module(mod_name)
            entry["status"] = "Loaded"
    port = 1
    while os.path.exists(os.path.join("/sys/kernel/config/nvmet/ports", str(port))):
        port += 1
    # Create the NVMe subsystem directory
    shell(f"mkdir -p /sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}")

    # Set the subsystem to accept any host
    shell(f"echo 1 | sudo tee /sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/attr_allow_any_host")

    # Create and configure the namespace
    shell(f"mkdir -p /sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/namespaces/{port}")
    shell(f"echo -n {NVME_DEVICE} | tee /sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/namespaces/{port}/device_path")
    shell(f"echo 1 | tee /sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/namespaces/{port}/enable")

    # Configure the NVMe-oF TCP port
    shell(f"mkdir -p /sys/kernel/config/nvmet/ports/{port}")
    shell(f"echo {IP_ADDRESS} | tee /sys/kernel/config/nvmet/ports/{port}/addr_traddr")
    shell(f"echo {TRTYPE} | tee /sys/kernel/config/nvmet/ports/{port}/addr_trtype")
    shell(f"echo {PORT_NUMBER} | tee /sys/kernel/config/nvmet/ports/{port}/addr_trsvcid")
    shell(f"echo {ADRFAM} | tee /sys/kernel/config/nvmet/ports/{port}/addr_adrfam")

    # Link the subsystem to the port
    shell(f"ln -s /sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME} /sys/kernel/config/nvmet/ports/{port}/subsystems/{SUBSYSTEM_NAME}")

    shell("nvme connect -t tcp -n testnqn -a 127.0.0.1 -s 4420")
    output = shell("nvme list -o json", capture_output=True)
    json_devices = json.loads(output.stdout)
    local_device = [device['DevicePath'] for device in json_devices['Devices'] if device["ModelNumber"] == "Linux"][0]
    shell(f"mkfs.ext4 {local_device}")
    shell("mkdir -p /mnt/nvme")
    shell(f"mount {local_device} /mnt/nvme")
    shell("echo 'foo' | tee /mnt/nvme/bar")

    yield local_device, "/mnt/nvme", "488"

    print("Teardown nvme device and clean up")
    shell("umount /mnt/nvme", ignore_exit_code=True)
    shell("rmdir /mnt/nvme", ignore_exit_code=True)
    shell(f"nvme disconnect -n {SUBSYSTEM_NAME}", ignore_exit_code=True)
    shell(f"rm {NVME_DEVICE}", ignore_exit_code=True)
    shell(f"echo 0 | sudo tee /sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/namespaces/{port}/enable")
    shell(f"echo 0 | sudo tee /sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/attr_allow_any_host")
    shell(f"rmdir /sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/namespaces/{port}")
    shell(f"unlink /sys/kernel/config/nvmet/ports/{port}/subsystems/{SUBSYSTEM_NAME}", ignore_exit_code=True)
    shell(f"rmdir /sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}")
    shell(f"rmdir /sys/kernel/config/nvmet/ports/{port}", ignore_exit_code=True)
    for entry in REQUIRED_NVME_MODULE:
        mod_name = entry["nvme_module"]
        if entry["status"] == "Loaded":
            module.unload_module(mod_name)
            entry["status"] = "None"
    if mount_package_installed == True:
        shell("DEBIAN_FRONTEND=noninteractive apt remove mount")
