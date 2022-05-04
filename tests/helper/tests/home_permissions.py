import logging

from helper import utils
from helper.exception import NotPartOfFeatureError, TestFailed, DisabledBy

logger = logging.getLogger(__name__)


class HomePermissions():
    """Class containing the test for checking if home permissions are correct"""
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
        test_is_disabled = utils.disabled_by(enabled_features, 'home_permissions')
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
            cls.instance = super(HomePermissions, cls).__new__(cls)

            # Initialize default test list of "home" directories
            test_dirs = ["/root"]

            # Get all defined home directories from passwd
            (exit_code, output, error) = client.execute_command(
                "cat /etc/passwd", quiet=True)

            for line in output.split('\n'):
                # Ignore empty newline
                if line != '':
                    line = line.split(":")
                    # Ignore services with UID below 1000
                    if int(line[2]) >= 1000:
                        test_dirs.append(line[5])

            # Get all defined home directories from default /home path
            (exit_code, output, error) = client.execute_command(
                "ls /home/", quiet=True)
            for line in output.split('\n'):
                home_dir = f"/home/{line}"
                if line != '' and home_dir not in test_dirs:
                    test_dirs.append(home_dir)

            # Validate permissions for all home directories
            for dir in test_dirs:
                (exit_code, output, error) = client.execute_command(
                    f"stat --format '%a' {dir}", quiet=True)
                # Make sure we do not test non existent directories
                if not "cannot statx" in error:
                    if dir == "/root":
                        if int(output) != 700:
                            msg_err = f"Permissions of {dir} is {output} instead of 700"
                            logger.error(msg_err)
                            raise TestFailed(msg_err)
                    else:
                        if not int(output) in (700, 750):
                            msg_err = f"Permissions of {dir} is {output} instead of 700 or 750"
                            logger.error(msg_err)
                            raise TestFailed(msg_err)

        return cls.instance
