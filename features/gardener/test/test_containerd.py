
import pytest
from helper.sshclient import RemoteClient


def test_containerd(client, non_chroot):
    """ Test if containerd capability """
    (exit_code, output, error) = client.execute_command("sudo systemctl enable containerd")
    assert exit_code == 0, f"no {error=} expected"

    (exit_code, output, error) = client.execute_command("sudo systemctl start containerd")
    assert exit_code == 0, f"no {error=} expected"

    (exit_code, output, error) = client.execute_command("sudo ctr image pull ghcr.io/gardenlinux/gardenlinux:nightly")
    assert exit_code == 0, f"no {error=} expected"

    (exit_code, output, error) = client.execute_command("sudo ctr run --rm -t ghcr.io/gardenlinux/gardenlinux:nightly gardenlinux echo 'hello from container'")
    assert exit_code == 0, f"no {error=} expected"
    assert output == "hello from container", f"unexpected output: {output}"
