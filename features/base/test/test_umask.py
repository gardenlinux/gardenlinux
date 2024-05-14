import pytest

def test_umask(client):
    cmd = f"sudo su root -c umask"
    (exit_code, output, error) = client.execute_command(
        cmd, quiet=True)
    assert exit_code == 0, f"Could not execute umask cmd: {error}"
    assert output == "0027\n", "umask is not set to 0027 "
