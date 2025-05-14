import pytest
import helper.utils as utils
import glob
import sys
import os
import logging
import tempfile

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


@pytest.fixture
def nvme_device(client, non_provisioner_chroot):
    utils.execute_remote_command(client, "truncate -s 512M /tmp/nvme.img")
    utils.execute_remote_command(client, "DEBIAN_FRONTEND=noninteractive sudo apt-get install -y mount")
    utils.execute_remote_command(client, "sudo losetup -fP /tmp/nvme.img")
    output = utils.execute_remote_command(client, """#!/bin/bash
# Define variables for the IP address, NVMe device, and subsystem name
IP_ADDRESS="127.0.0.1"
NVME_DEVICE="/tmp/nvme.img"
SUBSYSTEM_NAME="testnqn"
PORT_NUMBER="4420"
TRTYPE="tcp"
ADRFAM="ipv4"

# Load necessary kernel modules
sudo modprobe nvme_tcp
sudo modprobe nvmet
sudo modprobe nvmet-tcp

# Create the NVMe subsystem directory
sudo mkdir -p /sys/kernel/config/nvmet/subsystems/$SUBSYSTEM_NAME

# Set the subsystem to accept any host
echo 1 | sudo tee /sys/kernel/config/nvmet/subsystems/$SUBSYSTEM_NAME/attr_allow_any_host

# Create and configure the namespace
 mkdir -p /sys/kernel/config/nvmet/subsystems/$SUBSYSTEM_NAME/namespaces/1
echo -n $NVME_DEVICE | sudo tee /sys/kernel/config/nvmet/subsystems/$SUBSYSTEM_NAME/namespaces/1/device_path
echo 1 | sudo tee /sys/kernel/config/nvmet/subsystems/$SUBSYSTEM_NAME/namespaces/1/enable

# Configure the NVMe-oF TCP port
 mkdir -p /sys/kernel/config/nvmet/ports/1
echo $IP_ADDRESS | sudo tee /sys/kernel/config/nvmet/ports/1/addr_traddr
echo $TRTYPE | sudo tee /sys/kernel/config/nvmet/ports/1/addr_trtype
echo $PORT_NUMBER | sudo tee /sys/kernel/config/nvmet/ports/1/addr_trsvcid
echo $ADRFAM | sudo tee /sys/kernel/config/nvmet/ports/1/addr_adrfam

# Link the subsystem to the port
 ln -s /sys/kernel/config/nvmet/subsystems/$SUBSYSTEM_NAME /sys/kernel/config/nvmet/ports/1/subsystems/$SUBSYSTEM_NAME

echo "NVMe over Fabrics configuration is set up." """)

    print("Setup nvme device")
    logger.info(output)
    utils.execute_remote_command(client, "sudo nvme disconnect-all")
    output = utils.execute_remote_command(client, f"sudo nvme list -o json")
    logger.info(f"Nvme devices: %s", output)
    output = utils.execute_remote_command(
        client, "sudo nvme connect -t tcp -n testnqn -a 127.0.0.1 -s 4420",
        skip_error=True
    )
    logger.info(output)
    output = utils.execute_remote_command(client, "sudo mkfs.ext4 /dev/nvme0n1 || sudo nvme list -o json")
    logger.info("MKFS failed, nvme device list: %s", output)
    utils.execute_remote_command(client, "sudo mount /dev/nvme0n1 /mnt")
    utils.execute_remote_command(client, "echo 'foo' > /mnt/bar")

    yield "/dev/nvme0n1", "/mnt", "488"

    print("Teardown nvme device and clean up")
    utils.execute_remote_command(client, "sudo umount /mnt")
    utils.execute_remote_command(client, "sudo nvme disconnect-all")
    utils.execute_remote_command(client, "sudo rm /tmp/nvme.img")
    utils.execute_remote_command(client, "sudo rmmod nvme_tcp")


def test_nvme_locally(client, non_provisioner_chroot, nvme_device):
    """Check if nvme via tcp works with localhost"""

    device, mount_point, size = nvme_device
    output = utils.execute_remote_command(client, f"df -m | grep {mount_point}")
    split_output = [x.strip() for x in output.split(" ") if x]
    assert split_output[0] == device
    assert split_output[1] == size
    output = utils.execute_remote_command(client, f"cat /mnt/bar")
    assert output == "foo"
