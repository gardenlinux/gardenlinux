import logging

from helper import utils
from helper.exception import NotPartOfFeatureError, TestFailed, DisabledBy

logger = logging.getLogger(__name__)


class PasswordHashes():
    """Class containing the test for checking if debsums are available"""
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
        test_is_disabled = utils.disabled_by(enabled_features, 'password_hashes')
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
            cls.instance = super(PasswordHashes, cls).__new__(cls)

            # Call binary on remote and get content of file
            (exit_code, output, error) = client.execute_command(
                "cat /etc/pam.d/common-password", quiet=True)

            # Validate that the main part is present
            match_list = []
            for line in output.split('\n'):
                # First fetch the corresponding line(s)
                if "[success=1 default=ignore]" in line:
                    # Do not fetch comments
                    if not line.startswith("#"):
                        match_list.append(line)
                        test_line = line

            # Validate that this is only defined a single time
            # to ensure no feature has appended different options
            # multiple times
            if len(match_list) > 1:
                msg_err = "Redundant options defined in /etc/pam.d/common-password"
                logger.error(msg_err)
                raise TestFailed(msg_err)

            # Validate the entry for 'sha512' or 'yescrypt'
            if not 'yescrypt' or 'sha512' in test_line:
                msg_err = "No yescrypt or sha512 found in /etc/pam.d/common-password"
                logger.error(msg_err)
                raise TestFailed(msg_err) 

        return cls.instance
