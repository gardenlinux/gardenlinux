import pytest
from helper.utils import execute_remote_command


@pytest.mark.parametrize(
    "lsm,active",
    [
        ("selinux", False),
        ("apparmor", True),
    ]
)


def test_lsm(client, lsm, active, non_provisioner_chroot):
    out = execute_remote_command(client, "cat /sys/kernel/security/lsm")

    if active:
        assert lsm in out, "Expected LSM should be enabled: {lsm}"
    else:
        assert lsm not in out, "Expected LSM should NOT be enabled: {lsm}"
