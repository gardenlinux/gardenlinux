from helper.tests.systemctl import systemctl
import pytest

@pytest.mark.flaky(reruns=3, reruns_delay=10, only_rerun="AssertionError")
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
