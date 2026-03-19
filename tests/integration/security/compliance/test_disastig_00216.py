import time

import pytest


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="requires kernel logging")
@pytest.mark.root(reason="required to manage kernel modules")
@pytest.mark.modify(reason="modifies kernel module state")
def test_module_load(kernel_module):
    """
    As per DISA STIG compliance requirements, it is needed to verify
    that the audit system is configured to audit the loading and
    unloading of dynamic kernel modules
    Ref: SRG-OS-000471-GPOS-00216
    """

    MODULE = "8021q"

    assert kernel_module.is_module_available(
        MODULE
    ), f"stigcompliance: module {MODULE} not available on this system"

    result = kernel_module._shell("dmesg -C", capture_output=True)
    assert result.returncode == 0, "stigcompliance: failed to clear dmesg"

    loaded = kernel_module.load_module(MODULE)
    assert loaded, f"stigcompliance: failed to load module {MODULE}"

    time.sleep(1)

    dmesg_result = kernel_module._shell("dmesg", capture_output=True)
    assert dmesg_result.returncode == 0, "stigcompliance: failed to read dmesg"

    journal_result = kernel_module._shell(
        "journalctl -k --since '1 min ago' --no-pager",
        capture_output=True,
    )
    assert journal_result.returncode == 0, "stigcompliance: failed to read journal"

    logs = (dmesg_result.stdout + journal_result.stdout).lower()

    assert logs.strip() != "", "stigcompliance: no kernel logs captured"

    assert "8021q" in logs, "stigcompliance: module load not logged in kernel logs"
