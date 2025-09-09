#!/bin/bash
set -euxo pipefail

exec 3>&1 4>&2
exec > /dev/null 2>&1

SUBSYSTEM_NAME="testnqn"
NVME_DEVICE="/tmp/nvme.img"
IP_ADDRESS="127.0.0.1"
PORT_NUMBER="4420"
TRTYPE="tcp"
ADRFAM="ipv4"

if [ "$1" = "connect" ]; then
    truncate -s 512M /tmp/nvme.img
    DEBIAN_FRONTEND=noninteractive apt-get install -y mount
    losetup -fP /tmp/nvme.img
 
    modprobe nvme_tcp
    modprobe nvmet
    modprobe nvmet-tcp

    mkdir -p /sys/kernel/config/nvmet/subsystems/$SUBSYSTEM_NAME
    echo 1 > /sys/kernel/config/nvmet/subsystems/$SUBSYSTEM_NAME/attr_allow_any_host

    mkdir -p /sys/kernel/config/nvmet/subsystems/$SUBSYSTEM_NAME/namespaces/1
    echo -n "$NVME_DEVICE" > /sys/kernel/config/nvmet/subsystems/$SUBSYSTEM_NAME/namespaces/1/device_path
    echo 1 > /sys/kernel/config/nvmet/subsystems/$SUBSYSTEM_NAME/namespaces/1/enable

    mkdir -p /sys/kernel/config/nvmet/ports/1
    echo $IP_ADDRESS > /sys/kernel/config/nvmet/ports/1/addr_traddr
    echo $TRTYPE > /sys/kernel/config/nvmet/ports/1/addr_trtype
    echo $PORT_NUMBER > /sys/kernel/config/nvmet/ports/1/addr_trsvcid
    echo $ADRFAM > /sys/kernel/config/nvmet/ports/1/addr_adrfam

    ln -s /sys/kernel/config/nvmet/subsystems/$SUBSYSTEM_NAME /sys/kernel/config/nvmet/ports/1/subsystems/$SUBSYSTEM_NAME

    nvme connect -t tcp -n "$SUBSYSTEM_NAME" -a "$IP_ADDRESS" -s "$PORT_NUMBER"

    output=$(nvme list -o json)

    local_device=$(python3 -c "
import json
data = json.loads('''$output''')
devices = data.get('Devices', [])
linux_devs = [d['DevicePath'] for d in devices if d.get('ModelNumber') == 'Linux']
print(linux_devs[0] if linux_devs else '')
")

    if [ -z "$local_device" ]; then
        echo "Error: No local NVMe device found" >&4
        exit 1
    fi

    mkfs.ext4 "$local_device"
    mount "$local_device" /mnt
    echo 'foo' > /mnt/bar
    
    echo "$local_device, /mnt, 488" >&3
else
    umount /mnt || true
    nvme disconnect-all || true
    rm -f /tmp/nvme.img
    rmmod nvme_tcp || true
    echo "Disconnected and cleaned up"  >&3
fi
