import pytest
from helper.utils import execute_remote_command


@pytest.mark.parametrize(
    "pki_file",
    [
            "/etc/gardenlinux/gardenlinux-secureboot.pk.auth",
            "/etc/gardenlinux/gardenlinux-secureboot.kek.auth",
            "/etc/gardenlinux/gardenlinux-secureboot.db.auth"
    ]
)


def test_uefi_pki_files(client, pki_file):
    rc, out = execute_remote_command(client, f"stat {pki_file}", skip_error=True)
    err_msg = f"Could not find PKI file for secureboot: {pki_file}"
    assert rc == 0, f"{err_msg}"
