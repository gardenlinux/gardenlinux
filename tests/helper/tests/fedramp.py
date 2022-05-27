import logging
import os
import pytest
from helper import utils

logger = logging.getLogger(__name__)

def fedramp(client, test):
    """ Performing unit test for feature: Fedramp """

    # Create a temporary directory on remote
    dst_dir = utils.create_remote_tmp_dir(client)

    # Get filename from tests path
    file_name = os.path.basename(test)

    # Inject local files (from current container)
    # into the final image
    client.remote_path = f"{dst_dir}"
    client.bulk_upload([test])

    # Execute injected test files
    (exit_code, output, error) = client.execute_command(
        f"sh {dst_dir}/{file_name}", quiet=True)

    assert not "failed" in output, ("FedRAMP Test failed:")
