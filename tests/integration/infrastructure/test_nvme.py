from pathlib import Path

import pytest
from plugins.shell import ShellRunner


@pytest.mark.booted
@pytest.mark.root
@pytest.mark.modify
@pytest.mark.feature("nvme")
def test_nvme_locally(nvme_device, shell: ShellRunner):
    device, mount_dir, size = nvme_device
    mount_info_line = shell(f"df -m | grep {mount_dir}", capture_output=True)
    mount_info = [x.strip() for x in mount_info_line.stdout.split(" ") if x]
    assert mount_info[0] == device
    assert mount_info[1] == size
    assert Path(f"{mount_dir}/bar").read_text().strip() == "foo", "NVME Test failed"
