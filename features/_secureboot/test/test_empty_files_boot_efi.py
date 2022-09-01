from helper.utils import execute_remote_command


def test_empty_files_boot_efi(client):
    out = execute_remote_command(client, "find /boot/efi/ -type f")
    assert out == "", "/boot/efi/ is not empty."
