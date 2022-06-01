from helper.utils import execute_remote_command

import logging
logger = logging.getLogger(__name__)

def devices(client, device_opts):
    """ Checking that files in /dev corespond to a minimum set of requirements """
    # Iterate through all mandatory devices
    for opt in device_opts:
        # Split options to obtain only the device
        device = opt.split(",")
        device = device[0]

        # Get opts for specific device
        cmd = f"stat -c %u,%g,%F,%t,%T /dev/{device}"
        out = execute_remote_command(client, cmd)

        # Reformat string including its device name
        out = f"{device},{out}"

        assert out in device_opts, f"Device options are incorrect: {out} | should be {opt}" 
