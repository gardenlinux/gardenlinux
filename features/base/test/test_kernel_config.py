import pytest
from helper.utils import execute_remote_command
from helper.sshclient import RemoteClient
from helper.tests.file_content import file_content


def test_nvme_kernel_parameter(client, aws):
    """ Test for NVME kernel params """
    (exit_code, output, error) = client.execute_command("grep -c nvme_core.io_timeout=4294967295 /proc/cmdline")
    assert exit_code == 0, f"no {error=} expected"
    assert output.rstrip() == "1", "Expected 'nvme_core.io_timeout=4294967295' kernel parameter"


def test_for_kernel_address_space_layout_randomization(client):
    """
       We have to ensure that we have aslr enabled.
       Also, we ensure that we do not have a regression as we
       have seen it with the CVE-2024-6387 where a mistake combian
       with a regression causes a serias issue. 

       This was done with the help of the blog post from Justin Miller.
       https://zolutal.github.io/aslrnt/
    """

    check_for_kernel_setting()

    result = 0x0
    for _ in range(0,1000):
        # This can be optimzed.
        output = execute_remote_command(client, "cat /proc/self/maps | grep libc | head -n1")
        base_address = int(output.split('-')[0], 16)
        result |= base_address

    assert 0x7ffffffff000 == result, "ALSR regression detected!"

    result = 0x0
    for _ in range(0,1000):
        # This can be optimzed.
        output = execute_remote_command(client, "cat /proc/self/maps | grep ld | head -n1")
        base_address = int(output.split('-')[0], 16)
        result |= base_address
    assert 0x7ffffffff000 == result, "ALSR regression detected!"



def check_for_kernel_setting():
    """
       This will first check for the running configuration and 
       then for a written configuration. Only when there is 

    """
    pass
