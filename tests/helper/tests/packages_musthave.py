import logging

from helper import utils
from helper.exception import NotPartOfFeatureError
from helper.exception import TestFailed

logger = logging.getLogger(__name__)


class PackagesMusthave():
    failed_before = False
    def __new__(cls, client, features):
        if cls.failed_before:
            raise Exception("This test failed before in another feature")

        (enabledfeatures, myfeature) = features
        if myfeature in enabledfeatures:
            if not hasattr(cls, 'instance'):
                cls.instance = super(PackagesMusthave, cls).__new__(cls)

                pkgslist = utils.get_package_list(client)

                installed = utils.read_test_config(enabledfeatures, 'packages-musthave', '.list')

                musthave = []
                for line in installed:
                    if line not in pkgslist:
                        musthave.append(line)
                if not len(musthave) == 0:
                    cls.failed_before = True
                    raise TestFailed("%s are a musthave, but not installed" % (', '.join(musthave)))

        else:
            raise NotPartOfFeatureError("Feature %s this test belongs to is not enabled" % (myfeature))
            
        return cls.instance