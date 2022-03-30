import logging

import pytest

from helper.helper import Helper

logger = logging.getLogger(__name__)


def test_capabilities(client, features):
    (enabledfeatures, myfeature) = features
    if myfeature in enabledfeatures:
        if not pytest.capabilities_exec_already:
            pytest.capabilities_exec_already = True
            (exit_code, output, error) = client.execute_command("find /boot /etc /usr /var -type f -exec getcap {} \\;")
            assert exit_code == 0, f"no {error=} expected"

            capabilities = Helper.read_test_config(enabledfeatures, 'capabilities', '.list')

            cap_found = []
            cap_notfound = []
            for line in output.splitlines():
                if line not in capabilities:
                    cap_notfound.append(line)
                if line in capabilities:
                    cap_found.append(line)

            assert len(cap_found) == len(capabilities), "Found capabilities do not match expected capabilities. Found: %s Expected: %s" % (', '.join(cap_found), ', '.join(capabilities))
            assert len(cap_notfound) == 0, "Capabilities %s are not in expected capabilities list" % (', '.join(cap_notfound))
        else:
            pytest.skip("Test was already executed by another feature")
    else:
        pytest.skip("Feature %s this test belongs to is not enabled" % (myfeature))