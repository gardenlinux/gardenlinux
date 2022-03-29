import logging

import pytest

from helper.helper import Helper

logger = logging.getLogger(__name__)


def test_blacklisted_packages(client, features):
    (enabledfeatures, myfeature) = features
    if myfeature in enabledfeatures:
        if not pytest.blacklisted_packages_exec_already:
            pytest.blacklisted_packages_exec_already = True
            pkgslist = Helper.get_package_list(client)

            blklst = Helper.read_test_config(enabledfeatures, 'blacklisted-packages', '.list')

            blacklisted = []
            for line in blklst:
                if line in pkgslist:
                    blacklisted.append(line)
            assert len(blacklisted) == 0, "%s are blacklisted, but installed" % (', '.join(blacklisted))
        else:
            pytest.skip("Test was already executed by another feature")
    else:
        pytest.skip("Feature %s this test belongs to is not enabled" % (myfeature))
