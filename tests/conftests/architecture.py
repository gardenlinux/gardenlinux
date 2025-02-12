"""In here we keep the architecture we support or not"""


from sys import exit as sys_exit
from loggering import error as log_error

import pytest

@pytest.fixture
def non_amd64(client):
    (exit_code, output, error) = client.execute_command("dpkg --print-architecture", quiet=True)
    if exit_code != 0:
        log_error(error)
        sys_exit(exit_code)
    if "amd64" in output:
        pytest.skip('test not supported on amd64 architecture')

@pytest.fixture
def non_arm64(client):
    (exit_code, output, error) = client.execute_command("dpkg --print-architecture", quiet=True)
    if exit_code != 0:
        log_error(error)
        sys_exit(exit_code)
    if "arm64" in output:
        pytest.skip('test not supported on arm64 architecture')
