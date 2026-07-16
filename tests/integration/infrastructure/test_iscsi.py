import re
import time

import pytest
from plugins.block_devices import BlockDevices
from plugins.file import File
from plugins.parse import Parse
from plugins.shell import ShellRunner

# =============================================================================
# multipath Feature
# =============================================================================


@pytest.mark.testcov(
    [
        "GL-TESTCOV-multipath-config-multipath-conf",
    ]
)
@pytest.mark.feature("multipath")
def test_multipath_config_exists(file: File):
    """Test that multipath configuration exists"""
    assert file.is_regular_file(
        "/etc/multipath.conf"
    ), "Multipath configuration should exist"


# =============================================================================
# iscsi Feature - iSCSI Storage Configuration
# =============================================================================


@pytest.mark.testcov(
    [
        "GL-TESTCOV-iscsi-config-iscsi-initiatorname",
    ]
)
@pytest.mark.feature("iscsi")
@pytest.mark.booted(reason="iSCSI initiatorname.iscsi is created at boot time")
def test_iscsi_no_static_initiatorname(file: File):
    """Test that iSCSI does have an dynamically generated initiator name"""
    assert file.exists(
        "/etc/iscsi/initiatorname.iscsi"
    ), "iSCSI should have initiator name (generated dynamically)"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-iscsi-config-iscsi-node-session-auth-chap-algs",
    ]
)
@pytest.mark.feature("iscsi")
def test_iscsi_chap_algorithms_config_exists(parse: type[Parse]):
    """Test that iSCSI CHAP algorithms configuration exists"""
    content = parse.from_file("/etc/iscsi/iscsid.conf").parse(format="keyval")
    setting = "SHA3-256,SHA256,SHA1,MD5"
    assert (
        content["node.session.auth.chap_algs"] == setting
    ), f"iSCSI CHAP algorithms should be {setting}"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-iscsi-config-iscsi-node-session-scan",
    ]
)
@pytest.mark.feature("iscsi")
def test_iscsi_node_session_scan_config_exists(parse: type[Parse]):
    """Test that iSCSI node session scan configuration exists"""
    content = parse.from_file("/etc/iscsi/iscsid.conf").parse(format="keyval")
    setting = "manual"
    assert (
        content["node.session.scan"] == setting
    ), f"iSCSI node session scan should be {setting}"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-iscsi-config-iscsi-open-iscsi-configured",
    ]
)
@pytest.mark.feature("iscsi")
def test_iscsi_open_iscsi_configured(file: File):
    """Test that open-iscsi configured0 file exists"""
    assert file.exists(
        "/var/lib/open-iscsi-configured0"
    ), "Open-iSCSI configured0 file should exist"


@pytest.mark.booted(reason="iSCSI daemon is required")
@pytest.mark.root(reason="Needs to run iscsiadm")
@pytest.mark.modify(reason="Temporarily creates files and starts services")
@pytest.mark.feature("iscsi", reason="Feature test for iscsi")
def test_iscsi_setup(shell: ShellRunner, block_devices: BlockDevices, iscsi_device):
    assert not block_devices.contains(
        "iscsi-iqn", substring=True
    ), "Unexpected iscsi-iqn before rescan"

    session_id = shell("iscsiadm -m session | awk '{print $2}'", capture_output=True)
    session_id = re.fullmatch("\\[([0-9]+)\\]\n", session_id.stdout)
    assert session_id, "Failed to get session ID"
    session_id = session_id.group(1)

    shell(f"iscsiadm -m session -r {session_id} --rescan", capture_output=True)

    time.sleep(5)

    assert block_devices.contains(iscsi_device), f"Expected {iscsi_device} after rescan"
