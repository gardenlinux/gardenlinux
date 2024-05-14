import pytest

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


# Run the test unit to perform the
# final tests by the given artifact.
def test_umask(client, file, dict):
    # Check /etc/login.defs
    file_content(client, file, dict)

def test_umask_cmd(client, non_container):
    # Additionally check umask via cmd
    cmd = f"sudo su root -c umask"
    (exit_code, output, error) = client.execute_command(
        cmd, quiet=True)

    assert exit_code == 0, f"Could not execute umask cmd: {error}"
    assert output == "0027\n", "umask is not set to 0027 "
