import pytest
from helper.sshclient import RemoteClient
from helper.tests.file_content import file_content


def test_nvme_kernel_parameter(client, aws):
    """ Test for NVME kernel params """
    (exit_code, output, error) = client.execute_command("grep -c nvme_core.io_timeout=4294967295 /proc/cmdline")
    assert exit_code == 0, f"no {error=} expected"
    assert output.rstrip() == "1", "Expected 'nvme_core.io_timeout=4294967295' kernel parameter"
