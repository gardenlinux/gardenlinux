import logging
import string

logger = logging.getLogger(__name__)

def machine_id(client, chroot):
    (exit_code, output, error) = client.execute_command(
        "[[ ! -s /etc/machine-id ]] || cat /etc/machine-id", quiet=True)

    machine_id = output.strip(string.whitespace)

    assert exit_code == 0 and ( machine_id == "uninitialized" or
            machine_id == ""), "machine-id doesn't exist or is not empty!"