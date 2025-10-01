import logging
import time
import os

import pytest
from plugins.shell import ShellRunner

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

@pytest.mark.booted(reason="iSCSI daemon is required")
@pytest.mark.root(reason="Needs to run iscsiadm")
@pytest.mark.modify(reason="Deletes /etc/tgt/conf.d")
@pytest.mark.feature("iscsi", reason="Feature test for iscsi")
def test_iscsi_setup(shell: ShellRunner, iscsi_device):
    devices_before = os.listdir("/dev/disk/by-path")
    logger.info(f"Block devices before rescan: {", ".join(devices_before)}")
    assert not any(["iscsi-iqn" in device for device in devices_before]), "Unexpected iscsi-iqn before rescan"

    session_id = shell("sudo iscsiadm -m session | awk '{print $2}'", capture_output=True)
    session_id = session_id.stdout.strip("[]\n")
    assert session_id, "Failed to get session ID"

    output = shell(f"sudo iscsiadm -m session -r {session_id} --rescan", capture_output=True)
    logger.info(f"Rescan output: {output.stdout}")
    time.sleep(5)
    devices_after = os.listdir("/dev/disk/by-path")
    logger.info(f"Block devices after rescan: {", ".join(devices_after)}")
    assert any(["iscsi-iqn" in device for device in devices_after]), "Expected iscsi-iqn after rescan"
