import pytest
from helper.sshclient import RemoteClient
from helper.tests.file_content import file_content


@pytest.mark.parametrize(
    "args",
    [
        (   {
            # example expected kernel config options:
            #"CONFIG_INIT_ENV_ARG_LIMIT": "32",
            #"CONFIG_COMPILE_TEST": "is not set",
            #"CONFIG_WERROR": "n",
            #"CONFIG_LOCALVERSION": "",
            #"CONFIG_LOCALVERSION_AUTO": "is not set",
            #"CONFIG_HAVE_KERNEL_GZIP": "y"
            }
        )
    ]
)

def test_kernel_config(client, args, non_container):
    """compare kernel config options from the parametrize section with the
    kernel config options in the /boot/config-* file. The values 'is not set'
    and 'n' are treated as the same."""
    file = "/boot/config-*"
    file_content(client, file, args, ignore_comments=True)


def test_nvme_kernel_parameter(client, aws):
    """ Test for NVME kernel params """
    (exit_code, output, error) = client.execute_command("grep -c nvme_core.io_timeout=4294967295 /proc/cmdline")
    assert exit_code == 0, f"no {error=} expected"
    assert output.rstrip() == "1", "Expected 'nvme_core.io_timeout=4294967295' kernel parameter"
