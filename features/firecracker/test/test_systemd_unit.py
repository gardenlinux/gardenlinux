import pytest
from helper.utils import execute_remote_command
from helper.utils import validate_systemd_unit
from helper.utils import get_architecture


@pytest.mark.parametrize(
    "systemd_unit",
    [
        "rngd"
    ]
)


def test_systemd_unit(client, systemd_unit, non_provisioner_chroot):
    arch = get_architecture(client)
    active = True

    # We assume that on arm64, the systemd
    # unit should not be active after a start
    if arch == "arm64":
        active = False

    execute_remote_command(client, f"systemctl start {systemd_unit}")
    validate_systemd_unit(client, f"{systemd_unit}", active=active)
