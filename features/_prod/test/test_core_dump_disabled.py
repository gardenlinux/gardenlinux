import pytest
from helper.utils import execute_remote_command

@pytest.mark.security_id(965)
def test_check_for_coredump(client):
    soft_limit = execute_remote_command(client, "ulimit -S -c")
    assert soft_limit == '0'

    hard_limit = execute_remote_command(client, "ulimit -H -c")
    # As of now we have unlimited instead of 0.
    assert hard_limit == 'unlimited'
