import logging
from socketserver import ThreadingUnixStreamServer

from helper import utils
from helper.exception import NotPartOfFeatureError
from helper.exception import TestFailed

logger = logging.getLogger(__name__)


class Capabilities():
    failed_before = False
    def __new__(cls, client, features):
        if cls.failed_before:
            raise Exception("This test failed before in another feature")

        (enabledfeatures, myfeature) = features
        if myfeature in enabledfeatures:
            if not hasattr(cls, 'instance'):
                cls.instance = super(Capabilities, cls).__new__(cls)
                (exit_code, output, error) = client.execute_command("find /boot /etc /usr /var -type f -exec getcap {} \\;")
                assert exit_code == 0, f"no {error=} expected"

                capabilities = utils.read_test_config(enabledfeatures, 'capabilities', '.list')

                cap_found = []
                cap_notfound = []
                for line in output.splitlines():
                    if line not in capabilities:
                        cap_notfound.append(line)
                    if line in capabilities:
                        cap_found.append(line)

                if not len(cap_found) == len(capabilities):
                    cls.failed_before = True
                    raise TestFailed("Found capabilities do not match expected capabilities. Found: %s Expected: %s" % (', '.join(cap_found), ', '.join(capabilities)))

                if not len(cap_notfound) == 0:
                    cls.failed_before = True
                    raise TestFailed("Capabilities %s are not in expected capabilities list" % (', '.join(cap_notfound)))

        else:
            raise NotPartOfFeatureError("Feature %s this test belongs to is not enabled" % (myfeature))
            
        return cls.instance