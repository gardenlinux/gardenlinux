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
    shell(f"truncate -s 512M {NVME_DEVICE}", capture_output=True, ignore_exit_code=False)
    shell("DEBIAN_FRONTEND=noninteractive apt-get install -y mount", capture_output=True, ignore_exit_code=False)
    shell(f"losetup -fP {NVME_DEVICE}", capture_output=True, ignore_exit_code=False)

    # Load necessary kernel modules
    shell("modprobe nvme_tcp", capture_output=True, ignore_exit_code=False)
    shell("modprobe nvmet", capture_output=True, ignore_exit_code=False)
    shell("modprobe nvmet-tcp", capture_output=True, ignore_exit_code=False)

    # Create the NVMe subsystem directory
    shell(f"mkdir -p /sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}", capture_output=True, ignore_exit_code=False)

    # Set the subsystem to accept any host
    shell(f"echo 1 | sudo tee /sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/attr_allow_any_host", capture_output=True, ignore_exit_code=False)

    # Create and configure the namespace
    shell(f"mkdir -p /sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/namespaces/1", capture_output=True, ignore_exit_code=False)
    shell(f"echo -n {NVME_DEVICE} | tee /sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/namespaces/1/device_path", capture_output=True, ignore_exit_code=False)
    shell(f"echo 1 | tee /sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME}/namespaces/1/enable", capture_output=True, ignore_exit_code=False)

    # Configure the NVMe-oF TCP port
    shell("mkdir -p /sys/kernel/config/nvmet/ports/1", capture_output=True, ignore_exit_code=False)
    shell(f"echo {IP_ADDRESS} | tee /sys/kernel/config/nvmet/ports/1/addr_traddr", capture_output=True, ignore_exit_code=False)
    shell(f"echo {TRTYPE} | tee /sys/kernel/config/nvmet/ports/1/addr_trtype", capture_output=True, ignore_exit_code=False)
    shell(f"echo {PORT_NUMBER} | tee /sys/kernel/config/nvmet/ports/1/addr_trsvcid", capture_output=True, ignore_exit_code=False)
    shell(f"echo {ADRFAM} | tee /sys/kernel/config/nvmet/ports/1/addr_adrfam", capture_output=True, ignore_exit_code=False)

    # Link the subsystem to the port
    shell(f"ln -s /sys/kernel/config/nvmet/subsystems/{SUBSYSTEM_NAME} /sys/kernel/config/nvmet/ports/1/subsystems/{SUBSYSTEM_NAME}", capture_output=True, ignore_exit_code=False)

    output = shell("nvme connect -t tcp -n testnqn -a 127.0.0.1 -s 4420", capture_output=True, ignore_exit_code=False)
    output = shell("nvme list -o json", capture_output=True, ignore_exit_code=False)
    json_devices = json.loads(output.stdout)
    local_device = [device['DevicePath'] for device in json_devices['Devices'] if device["ModelNumber"] == "Linux"][0]
    shell(f"mkfs.ext4 {local_device}", capture_output=True, ignore_exit_code=False)
    shell(f"mount {local_device} /mnt/nvme", capture_output=True, ignore_exit_code=False)
    shell("echo 'foo' | tee /mnt/nvme/bar", capture_output=True, ignore_exit_code=False)

    yield local_device, "/mnt/nvme", "488"

    print("Teardown nvme device and clean up")
    shell("umount /mnt/nvme")
    shell("nvme disconnect-all")
    shell(f"rm {NVME_DEVICE}")
    shell("rmmod nvme_tcp")
