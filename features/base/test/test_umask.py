import pytest
from helper.tests.file_content import file_content

# Parametrize the test unit with further
# options.
# First: File to process
# Second: Key to search
# Third: Value of Key
@pytest.mark.parametrize(
    "file,dict",
    [
        ("/etc/login.defs", {"UMASK": "027"})
    ]
)


# pam_umask reads the umask value from /etc/login.defs,
# therefore we need to test the UMASK default value set via /etc/login.defs
def test_umask(client, file, dict):
    # Check /etc/login.defs
    file_content(client, file, dict)

# `/root/.bashrc`, `/root/.profile`, ... can overwrite default value from /etc/login.defs
# therefore we need to check via the umask cmd in root bash environment
def test_umask_cmd(client, non_container):
    cmd = f"sudo su root -c umask"
    (exit_code, output, error) = client.execute_command(
        cmd, quiet=True)

    assert exit_code == 0, f"Could not execute umask cmd: {error}"
    assert output == "0027\n", "umask is not set to 0027 "
