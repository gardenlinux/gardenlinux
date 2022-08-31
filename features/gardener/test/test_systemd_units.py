import pytest
from helper.utils import execute_remote_command
from helper.utils import validate_systemd_unit


@pytest.mark.parametrize(
    "systemd_unit",
    [
        "containerd",
        "docker",
    ]
)


def test_systemd_unit(client, systemd_unit, non_chroot):
    execute_remote_command(client, f"sudo -u root systemctl start {systemd_unit}")
    validate_systemd_unit(client, f"{systemd_unit}")
