import pytest
from plugins.shell import ShellRunner
import json

# Define variables for the IP address, NVMe device, and subsystem name
IP_ADDRESS="127.0.0.1"
NVME_DEVICE="/tmp/nvme.img"
SUBSYSTEM_NAME="testnqn"
PORT_NUMBER="4420"
TRTYPE="tcp"
ADRFAM="ipv4"

@pytest.fixture
def nvme_device(shell: ShellRunner):
    shell(f"truncate -s 512M {NVME_DEVICE}")
    shell("DEBIAN_FRONTEND=noninteractive apt-get install -y mount")
    shell(f"losetup -fP {NVME_DEVICE}")

    # Load necessary kernel modules
    shell("modprobe nvme_tcp")
    shell("modprobe nvmet")
    shell("modprobe nvmet-tcp")

    # Create the NVMe subsystem directory
    shell(f"mkdir -p /sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}")

    # Set the subsystem to accept any host
    shell(f"echo 1 | sudo tee /sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/attr_allow_any_host")

    # Create and configure the namespace
    shell(f"mkdir -p /sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/namespaces/1")
    shell(f"echo -n {NVME_DEVICE} | tee /sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/namespaces/1/device_path")
    shell(f"echo 1 | tee /sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/namespaces/1/enable")

    # Configure the NVMe-oF TCP port
    shell("mkdir -p /sys/kernel/config/nvmet/ports/1")
    shell(f"echo {IP_ADDRESS} | tee /sys/kernel/config/nvmet/ports/1/addr_traddr")
    shell(f"echo {TRTYPE} | tee /sys/kernel/config/nvmet/ports/1/addr_trtype")
    shell(f"echo {PORT_NUMBER} | tee /sys/kernel/config/nvmet/ports/1/addr_trsvcid")
    shell(f"echo {ADRFAM} | tee /sys/kernel/config/nvmet/ports/1/addr_adrfam")

    # Link the subsystem to the port
    shell(f"ln -s /sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME} /sys/kernel/config/nvmet/ports/1/subsystems/{SUBSYSTEM_NAME}")

    shell("nvme connect -t tcp -n testnqn -a 127.0.0.1 -s 4420")
    output = shell("nvme list -o json", capture_output=True)
    json_devices = json.loads(output.stdout)
    local_device = [device['DevicePath'] for device in json_devices['Devices'] if device["ModelNumber"] == "Linux"][0]
    shell(f"mkfs.ext4 {local_device}")
    shell(f"mount {local_device} /mnt/nvme")
    shell("echo 'foo' | tee /mnt/nvme/bar")

    yield local_device, "/mnt/nvme", "488"

    print("Teardown nvme device and clean up")
    shell("umount /mnt/nvme", ignore_exit_code=True)
    shell("nvme disconnect-all", ignore_exit_code=True)
    shell(f"rm {NVME_DEVICE}", ignore_exit_code=True)
    shell("rmmod nvme_tcp", ignore_exit_code=True)
