import logging

from helper import utils
from helper.exception import NotPartOfFeatureError, TestFailed, DisabledBy

logger = logging.getLogger(__name__)


class SGIDSUID():
    """Class containing the test to find SGID and SUID files"""
    failed_before = False
    def __new__(cls, client, features):
        """The actual test.
        Placing the code for the test in the __new__ method allows to test if
        there is already an instance of this class and avoid executing the
        test more than once.
        The class variable failed_before is used to make sure the test is
        shown as failed when the first call of the test had failed.
        If the test had passed the first time and is called again the same
        instance is returned and the test is shown as passed, but the test is
        NOT executed again. Therefore the test collects the test configuration
        from all enabled features, so it is not necessary to executed the test
        more than once.
        """

        # throws exception if the test had failed before to make sure it is
        # not show as passed when called again by another feature.
        if cls.failed_before:
            raise Exception("This test failed before in another feature")

        (enabled_features, my_feature) = features

        # check if test is disabled in a feature
        test_is_disabled = utils.disabled_by(enabled_features, 'sgid_suid')
        if not len(test_is_disabled) == 0:
            raise DisabledBy("Test is explicitly disabled by features " +
                f"{', '.join(test_is_disabled)}")

        # check if the test is part of the features used to build the
        # gardenlinux image
        if my_feature not in enabled_features:
            raise NotPartOfFeatureError(
                f"Feature {my_feature} this test belongs to is not enabled")

        # first check if there is already an instance of this class, if it is
        # the first time this instance is initiated add the class variable
        # instance containing the instance itself and then do the actual
        # testing. 
        if not hasattr(cls, 'instance'):
            cls.instance = super(SGIDSUID, cls).__new__(cls)

            # Load the features YAML config file
            feature_config = utils.get_feature_config(my_feature)

            # Find SGID files
            sgid_whitelist = feature_config[my_feature]["sgid"]["whitelist"]
            sgid_found = []
            cmd = "find / -type f -perm -2000 -exec stat -c '%n,%u,%g' {} \; 2> /dev/null"
            (exit_code, output, error) = client.execute_command(
                cmd, quiet=True)

            for line in output.split('\n'):
                if line != '':
                    sgid_found.append(line)

            sgid_diff = set(sgid_found) - set(sgid_whitelist)
            if len(list(sgid_diff)) > 0:
                msg_err = f"Following SGID files were found: {sgid_diff}"
                logger.error(msg_err)
                raise TestFailed(msg_err)

            # Find SUID files
            suid_whitelist = feature_config[my_feature]["suid"]["whitelist"]
            suid_found = []
            cmd = "find / -type f -perm -4000 -exec stat -c '%n,%u,%g' {} \; 2> /dev/null"
            (exit_code, output, error) = client.execute_command(
                cmd, quiet=True)

            for line in output.split('\n'):
                if line != '':
                    suid_found.append(line)

            suid_diff = set(suid_found) - set(suid_whitelist)
            if len(list(suid_diff)) > 0:
                msg_err = f"Following SUID files were found: {suid_diff}"
                logger.error(msg_err)
                raise TestFailed(msg_err)

        return cls.instance
