"""We define the fixtures here, that we can use to turn off tests for architectures."""


from sys import exit as sys_exit
from logging import error as log_error

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
