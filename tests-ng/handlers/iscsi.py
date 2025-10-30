import os
import re
from doctest import FAIL_FAST
from math import fabs

import pytest
from plugins.kernel_module import KernelModule
from plugins.shell import ShellRunner
from plugins.systemd import Systemd

REQUIRED_NVME_MODULE = [
    {"nvme_module": "libiscsi", "status": None},
    {"nvme_module": "libiscsi_tcp", "status": None},
    {"nvme_module": "iscsi_tcp", "status": None},
    {"nvme_module": "sd_mod", "status": None},
    {"nvme_module": "sg", "status": None},
]

disk_attributes = re.compile(
    "Login to \\[iface: default, target: ([^,]*), portal: ([.0-9]*),([0-9]*)\\] successful."
)


@pytest.fixture
def iscsi_device(shell: ShellRunner, systemd: Systemd, kernel_module: KernelModule):
    for entry in REQUIRED_NVME_MODULE:
        mod_name = entry["nvme_module"]
        if not kernel_module.is_module_loaded(mod_name):
            kernel_module.load_module(mod_name)
            entry["status"] = "Loaded"

    stop_tgt = False
    if not systemd.is_active("tgt"):
        systemd.start_unit("tgt")

    shell("dd if=/dev/zero of=/tmp/iscsi_disk.img bs=1 count=0 seek=1G")

    iscsi_config = """<target iqn.2025-04.localhost:storage.disk1>
            backing-store /tmp/iscsi_disk.img
            initiator-address 127.0.0.1
        </target>"""

    remove_conf_d = False
    if not os.path.isdir("/etc/tgt/conf.d"):
        os.mkdir("/etc/tgt/conf.d")
        remove_conf_d = True

    with open("/etc/tgt/conf.d/iscsi_target_test.conf", "w") as f:
        f.write(iscsi_config)

    shell("/usr/sbin/tgt-admin --update ALL")
    shell("tgtadm --mode target --op show")
    shell("iscsiadm -m discovery -t sendtargets -p 127.0.0.1")
    out = shell("iscsiadm -m node --login", capture_output=True)
    attributes = disk_attributes.findall(out.stdout)
    disk_name = "name_not_found_in_iscsi_handler"
    if len(attributes) == 1:
        name, ip, port = attributes[0]
        disk_name = f"ip-{ip}:{port}-iscsi-{name}-lun-1"

    yield disk_name

    shell("iscsiadm --mode node --logout")
    if stop_tgt:
        systemd.stop_unit("tgt")

    os.remove("/etc/tgt/conf.d/iscsi_target_test.conf")
    if remove_conf_d:
        os.rmdir("/etc/tgt/conf.d")

    for entry in reversed(REQUIRED_NVME_MODULE):
        mod_name = entry["nvme_module"]
        if entry["status"] == "Loaded":
            kernel_module.unload_module(mod_name)
            entry["status"] = "None"
