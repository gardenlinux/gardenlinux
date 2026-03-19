import time

import pytest


@pytest.mark.feature(
    "not container and not gardener and not lima and not capi and not baremetal"
)
@pytest.mark.booted(reason="requires kernel logging")
@pytest.mark.root(reason="required to manage kernel modules")
@pytest.mark.modify(reason="modifies kernel module state")
def test_kernel_module_load_logged(kernel_module, shell):
    """
    As per DISA STIG compliance requirements, it is needed to verify
    that the audit system is configured to audit the loading and
    unloading of dynamic kernel modules
    Ref: SRG-OS-000471-GPOS-00216
    """

    MODULE = "8021q"

    if not kernel_module.is_module_available(MODULE):
        return

    kernel_module.load_module(MODULE)

    time.sleep(1)

    dmesg_result = shell("dmesg", capture_output=True)
    assert dmesg_result.returncode == 0, "stigcompliance: failed to read dmesg"

    journal_result = shell(
        "journalctl -k --since '1 min ago' --no-pager",
        capture_output=True,
    )
    assert journal_result.returncode == 0, "stigcompliance: failed to read journal"

    logs = (dmesg_result.stdout + journal_result.stdout).lower()

    assert logs.strip(), "stigcompliance: no kernel logs captured"

    assert "802.1q" in logs, "stigcompliance: kernel module load event not logged"
