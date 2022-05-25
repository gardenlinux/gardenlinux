from helper.tests.debsums import debsums
import pytest

@pytest.mark.parametrize(
    "exclude",
    [
        [
            "/lib/systemd/system/dbus.socket",
            "/usr/share/pam-configs/cracklib"
        ]
    ]
)

def test_debsums(client, exclude):
    debsums(client, exclude)