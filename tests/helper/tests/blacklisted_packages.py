import logging

from helper import utils
from helper.exception import NotPartOfFeatureError
from helper.exception import TestFailed

logger = logging.getLogger(__name__)


class BlacklistedPackages():
    failed_before = False
    def __new__(cls, client, features):
        if cls.failed_before:
            raise Exception("This test failed before in another feature")

        (enabledfeatures, myfeature) = features
        if myfeature in enabledfeatures:
            if not hasattr(cls, 'instance'):
                cls.instance = super(BlacklistedPackages, cls).__new__(cls)

                pkgslist = utils.get_package_list(client)

                blklst = utils.read_test_config(enabledfeatures, 'blacklisted-packages', '.list')

                blacklisted = []
                for line in blklst:
                    if line in pkgslist:
                        blacklisted.append(line)

                if not len(blacklisted) == 0:
                    cls.failed_before = True
                    raise TestFailed("%s are blacklisted, but installed" % (', '.join(blacklisted)))
        else:
            raise NotPartOfFeatureError("Feature %s this test belongs to is not enabled" % (myfeature))
            
        return cls.instance