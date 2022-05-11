import logging
import string

logger = logging.getLogger(__name__)

def kernel_parameter(client, parameter, value):

    (exit_code, output, error) = client.execute_command(
        f"sysctl -n {parameter}", quiet=True)
    assert exit_code == 0, f"no {error=} expected"

    running_value = output.strip(string.whitespace)
    assert running_value == str(value), (f"{parameter} is not " +
                    f"configured correctly. Expected " +
                    f"{parameter} set to {value}.")
                    