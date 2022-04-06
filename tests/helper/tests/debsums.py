import logging

from helper import utils
from helper.exception import NotPartOfFeatureError, TestFailed, DisabledBy

logger = logging.getLogger(__name__)


class Debsums():
    """Class containing the test for checking if debsums are available"""
    failed_before = False
    def __new__(cls, client, features):
        """The actual test.
        Placing the code for the test in the __new__ method allows to test if there is already an instance of this class
        and avoid executing the test more than once.
        The class variable failed_before is used to make sure the test is shown as failed when the first call of the test had
        failed.
        If the test had passed the first time and is called again the same instance is returned and the test is shown as passed,
        but the test is NOT executed again. Therefore the test collects the test configuration from all enabled features, so it
        is not necessary to executed the test more than once."""

        # throws exception if the test had failed before to make sure it is not show as passed when called again by another feature.
        if cls.failed_before:
            raise Exception("This test failed before in another feature")

        (enabledfeatures, myfeature) = features

        # check if test is disabled in a feature
        test_is_disabled = utils.is_disabled(enabledfeatures, 'debsums')
        if not len(test_is_disabled) == 0:
            raise DisabledBy("Test is explicitly disabled by features %s" % (', '.join(test_is_disabled)))

        # check if the test is part of the features used to build the gardenlinux image
        if myfeature in enabledfeatures:

            # first check if there is already an instance of this class, if it is the first time this instance is initiated
            # add the class variable instance containing the instance itself and then do the actual testing. 
            if not hasattr(cls, 'instance'):
                cls.instance = super(Debsums, cls).__new__(cls)

                utils.AptUpdate(client)                
                (exit_code, output, error) = client.execute_command("apt-get install -y --no-install-recommends debsums apt-utils")
                assert exit_code == 0, f"no {error=} expected"

                debsums_exclude = utils.read_test_config(enabledfeatures, 'debsums', '_exclude.list')

                (exit_code, output, error) = client.execute_command("debsums -l")
                assert exit_code == 0, f"no {error=} expected"

                if not output == '':
                    cls.failed_before = True
                    raise TestFailed("the following packages don't have md5sums: %s" % (output))

                (exit_code, output, error) = client.execute_command("debsums -sc")
                assert exit_code == 0 or exit_code == 2, f"no {error=} expected"
                
                changed = []
                for line in error.splitlines():
                    if line.split()[3] not in debsums_exclude:
                        changed.append(line.split()[3] + " " + line.split()[4] + " " + line.split()[5] + " " + line.split()[6])

                if not len(changed) == 0:
                    cls.failed_before = True
                    raise TestFailed("the following files have changes: %s " % (', '.join(changed)))

        else:
            raise NotPartOfFeatureError("Feature %s this test belongs to is not enabled" % (myfeature))
            
        return cls.instance