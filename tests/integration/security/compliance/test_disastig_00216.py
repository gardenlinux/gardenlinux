import time

import pytest
from plugins.shell import ShellRunner

@pytest.fixture
def module_cleanup(shell: ShellRunner):
    before = shell("lsmod", capture_output=True).stdout
    yield
    after = shell("lsmod", capture_output=True).stdout

    before_set = {line.split()[0] for line in before.splitlines()[1:]}
    after_set = {line.split()[0] for line in after.splitlines()[1:]}

    new_modules = after_set - before_set

    for module in new_modules:
        shell(f"modprobe -r {module} || true")

@pytest.mark.feature("not container")
@pytest.mark.booted(reason="requires kernel logging")
@pytest.mark.root(reason="required to manage kernel modules")
@pytest.mark.modify(reason="modifies kernel module state")
def test_module_load(shell: ShellRunner, module_cleanup):
    """
    Verify kernel module load generates logs
    Ref: SRG-OS-000471-GPOS-00216
    """

    MODULE = "8021q"

    shell(f"modprobe -r {MODULE} || true")

    shell("dmesg -C")

    shell(f"modprobe {MODULE}")

    time.sleep(1)

    dmesg = shell("dmesg", capture_output=True).stdout
    journal = shell(
        "journalctl -k --since '1 min ago' --no-pager",
        capture_output=True,
    ).stdout

    logs = (dmesg + journal).lower()

    assert logs.strip() != "", "stigcompliance: no kernel logs captured"
    assert "8021q" in logs, "stigcompliance: module load not logged"