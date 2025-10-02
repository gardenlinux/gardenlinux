import pytest
import logging
import os
import shutil
import time
from .shell import ShellRunner

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

@pytest.fixture
def iscsi_device(shell: ShellRunner):
    logger.info("Starting iSCSI setup test")
    shell("/usr/sbin/start-stop-daemon --start --exec /usr/sbin/tgtd || /bin/true")

    shell("dd if=/dev/zero of=/tmp/iscsi_disk.img bs=1 count=0 seek=1G")

    iscsi_config = """<target iqn.2025-04.localhost:storage.disk1>
            backing-store /tmp/iscsi_disk.img
            initiator-address 127.0.0.1
        </target>"""
    shell("sudo mkdir -p /etc/tgt/conf.d")
    os.makedirs("/etc/tgt/conf.d", exist_ok=True)
    with open("/etc/tgt/conf.d/iscsi_target.conf", "w") as f:
        f.write(iscsi_config)
    
    shell("sudo /usr/sbin/tgt-admin --update ALL")
    shell("sudo tgtadm --mode target --op show")
    shell("sudo iscsiadm -m discovery -t sendtargets -p 127.0.0.1")
    output = shell("sudo iscsiadm -m node --login", capture_output=True)
    logger.info(f"iscsiadm login: {output.stdout}")
    time.sleep(10)

    yield

    shell("sudo iscsiadm --mode node --logout")
    shell("/usr/sbin/start-stop-daemon --stop --quiet --oknodo --exec /usr/sbin/tgtd")
    shutil.rmtree("/etc/tgt/conf.d")
