import logging

import pytest

from helper.helper import Helper

logger = logging.getLogger(__name__)


def test_packages_musthave(client, features):
    (enabledfeatures, myfeature) = features
    if myfeature in enabledfeatures:
        if not pytest.package_musthave_exec_already:
            pytest.package_musthave_exec_already = True
            pkgslist = Helper.get_package_list(client)

            installed = Helper.read_test_config(enabledfeatures, 'packages-musthave', '.list')

            musthave = []
            for line in installed:
                if line not in pkgslist:
                    musthave.append(line)
            assert len(musthave) == 0, "%s are a musthave, but not installed" % (', '.join(musthave))
        else:
            pytest.skip("Test was already executed by another feature")
    else:
        pytest.skip("Feature %s this test belongs to is not enabled" % (myfeature))
