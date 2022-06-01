import pytest
from helper.tests.devices import devices


@pytest.mark.parametrize(
    "device_opts",
    [
        [
            "console,0,5,character special file,88,0", #chroot
            "console,0,0,character special file,5,1",
            "fd,0,0,symbolic link,0,0",
            "full,0,0,character special file,1,7",
            "null,0,0,character special file,1,3",
            "ptmx,0,0,character special file,5,2",
            "ptmx,0,0,symbolic link,0,0", #chroot
            "pts,0,0,directory,0,0",
            "random,0,0,character special file,1,8",
            "shm,0,0,directory,0,0",
            "stderr,0,0,symbolic link,0,0",
            "stdin,0,0,symbolic link,0,0",
            "stdout,0,0,symbolic link,0,0",
            "tty,0,0,character special file,5,0",
            "urandom,0,0,character special file,1,9",
            "zero,0,0,character special file,1,5"
        ]
    ]
)


def test_devices(client, device_opts):
    devices(client, device_opts)
