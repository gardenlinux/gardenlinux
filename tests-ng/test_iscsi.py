import time

import pytest
from handlers.iscsi import iscsi_device
from plugins.block_devices import BlockDevices
from plugins.shell import ShellRunner


@pytest.mark.booted(reason="iSCSI daemon is required")
@pytest.mark.root(reason="Needs to run iscsiadm")
@pytest.mark.modify(reason="Temporarily creates files and starts services")
@pytest.mark.feature("iscsi", reason="Feature test for iscsi")
def test_iscsi_setup(shell: ShellRunner, block_devices: BlockDevices, iscsi_device):
    assert not block_devices.contains(
        "iscsi-iqn", substring=True
    ), "Unexpected iscsi-iqn before rescan"

    session_id = shell(
        "sudo iscsiadm -m session | awk '{print $2}'", capture_output=True
    )
    session_id = session_id.stdout.strip("[]\n")
    assert session_id, "Failed to get session ID"

    shell(f"iscsiadm -m session -r {session_id} --rescan", capture_output=True)

    time.sleep(5)

    assert block_devices.contains(iscsi_device), f"Expected {iscsi_device} after rescan"
