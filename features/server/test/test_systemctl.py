from helper.tests.systemctl import systemctl
import pytest

@pytest.mark.parametrize(
    "state, services",
    [
        ("enabled", [
                    "systemd-networkd.service",
                    "auditd.service"
                    ]
        ),
        ("disabled", []
        )
    ]
)

def test_systemctl(client, state, services):
    systemctl(client, state, services)