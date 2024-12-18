import pytest
from helper.utils import execute_remote_command, get_architecture
from helper.sshclient import RemoteClient
from helper.tests.file_content import file_content


def test_nvme_kernel_parameter(client, aws):
    """ Test for NVME kernel params """
    (exit_code, output, error) = client.execute_command("grep -c nvme_core.io_timeout=4294967295 /proc/cmdline")
    assert exit_code == 0, f"no {error=} expected"
    assert output.rstrip() == "1", "Expected 'nvme_core.io_timeout=4294967295' kernel parameter"


@pytest.mark.security_id(963)
def test_for_restricted_access_to_dmesg(client):
    dmesg_restrict = check_for_kernel_setting(client, "kernel.dmesg_restrict")
    assert dmesg_restrict == "1", "dmesg wasn't restircted!"


@pytest.mark.security_id(964)
def test_for_restricted_soft_and_hardlinks(client):
    symlinks = check_for_kernel_setting(client, "fs.protected_symlinks")
    hardlinks = check_for_kernel_setting(client, "fs.protected_hardlinks")

    assert symlinks == "1", " symlink arn't restricted!"
    assert hardlinks == "1", "hardlinks arn't restricted!"


@pytest.mark.security_id(962)
def test_for_kernel_address_space_layout_randomization(client):
    """
       We have to ensure that we have ASLR enabled.

    """
    randomize_va_space = check_for_kernel_setting(client, "kernel.randomize_va_space")
    assert randomize_va_space == "2", "ASLR wasn't set!"


def test_for_regression_in_kernel_address_space_layout_randomization(client):
    """
       Also, we ensure that we do not have a regression, as we 
       have seen it with the CVE-2024-6387 where a mistake in SSH 
       in combination with weak or no ALSR caused a series vulnerability.

       This was done with the help of the blog post from Justin Miller.
       https://zolutal.github.io/aslrnt/
    """
    arch = get_architecture(client)
    match arch:
        case "arm64":
            expected_values = [0xfffffffff000, 0xffffffff0000 ]
        case "amd64":
            expected_values = [0x7ffffffff000]

    result = 0x0
    # We had this in a seperate for loop, however, this will create thound ssh connections
    # and that's very slow.
    output = execute_remote_command(client, "for n in $(seq 0 1000); do cat /proc/self/maps | grep libc | head -n 1;done |awk '{print $1}'")
    for _ in output.split("\n"):
        base_address = int(_.split('-')[0], 16)
        result |= base_address

    assert [mem_adr for mem_adr in expected_values if result in expected_values], "ASLR regression detected!"

    result = 0x0
    output = execute_remote_command(client, "for n in $(seq 0 1000); do cat /proc/self/maps | grep ld | head -n 1;done |awk '{print $1}'")
    for _ in output.split("\n"):
        base_address = int(_.split('-')[0], 16)
        result |= base_address

    assert [mem_adr for mem_adr in expected_values if result in expected_values], "ASLR regression detected!"



def check_for_kernel_setting(client, sysctl_variable):
    """
       This will check for the running configuration.
    """
    output = execute_remote_command(client, f"sysctl {sysctl_variable}")
    return output.split("=")[1].strip()

