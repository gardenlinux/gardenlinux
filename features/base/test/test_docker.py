import pytest
from helper.sshclient import RemoteClient


def test_docker(client, non_chroot):
    """ Test for docker capability """
    (exit_code, output, error) = client.execute_command("grep GARDENLINUX_FEATURES /etc/os-release | grep gardener", quiet=True)
    if exit_code != 0:
        pytest.skip("test_docker needs the gardenlinux feature gardener to be enabled")
    (exit_code, output, error) = client.execute_command("sudo systemctl start docker")
    if exit_code != 0:
        (journal_rc, output, error) = client.execute_command("sudo journalctl --no-pager -xu docker.service")
    assert exit_code == 0, f"no {error=} expected"
    (exit_code, output, error) = client.execute_command("sudo docker run --rm alpine:latest ash -c 'echo from container'")
    assert exit_code == 0, f"no {error=} expected"
    assert output == "from container\n", f"Expected 'from container' output but got {output}"
