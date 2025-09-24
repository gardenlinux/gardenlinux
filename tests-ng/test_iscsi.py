import logging
import time

import pytest
from plugins.shell import ShellRunner

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

@pytest.mark.booted(reason="iSCSI daemon is required")
@pytest.mark.root(reason="Needs to run iscsiadm")
@pytest.mark.modify(reason="Deletes /etc/tgt/conf.d")
@pytest.mark.feature("iscsi", reason="Feature test for iscsi")
def test_iscsi_setup(shell: ShellRunner, iscsi_device):
    output_before = shell("ls -la /dev/disk/by-path/", capture_output=True)
    logger.info(f"Block devices before rescan: {output_before.stdout}")
    assert "iscsi-iqn" not in output_before.stdout, "Unexpected iscsi-iqn before rescan"

    session_id = shell("sudo iscsiadm -m session | awk '{print $2}'", capture_output=True)
    session_id = session_id.stdout.strip("[]\n")
    assert session_id, "Failed to get session ID"

    output = shell(f"sudo iscsiadm -m session -r {session_id} --rescan", capture_output=True)
    logger.info(f"Rescan output: {output.stdout}")
    time.sleep(5)
    output_after = shell("ls -la /dev/disk/by-path/", capture_output=True)
    logger.info(f"Block devices after rescan: {output_after.stdout}")
    assert "iscsi-iqn" in output_after.stdout, "Expected iscsi-iqn after rescan"
