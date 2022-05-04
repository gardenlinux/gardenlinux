import logging

from helper import utils
from helper.exception import NotPartOfFeatureError, TestFailed, DisabledBy

logger = logging.getLogger(__name__)


class TestUsers():
    """Class containing the tests based on /etc/passwd file"""
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
        test_is_disabled = utils.disabled_by(enabled_features, 'TestUsers')
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
            cls.instance = super(TestUsers, cls).__new__(cls)

            # Get content from /etc/passwd
            (exit_code, output, error) = client.execute_command(
                "getent passwd", quiet=True)

            for line in output.split('\n'):
                # Ignore empty newline
                if line != '':
                    line = line.split(":")

                    # There should NOT be any user present
                    # except of 'dev' from dev feature or 'nobody' from nfs
                    # https://github.com/gardenlinux/gardenlinux/issues/854
                    if int(line[2]) >= 1000 and line[0] not in ["dev", "nobody"]:
                        user = line[0]
                        msg_err = f"Unexpected user account found in /etc/passwd: {user}"
                        logger.error(msg_err)
                        raise TestFailed(msg_err)

                    # Serviceaccounts should NOT have a valid shell
                    # except of 'root' (gid: 0) and 'sync' (gid: 65534)
                    # https://github.com/gardenlinux/gardenlinux/issues/814
                    if int(line[2]) < 1000 and line[6] not in ['/usr/sbin/nologin', '/bin/false'] \
                            and int(line[3]) not in [0, 65534]:
                        user = line[0]
                        msg_err = f"Unexpected shell found in /etc/passwd for user/service: {user}"
                        logger.error(msg_err)
                        raise TestFailed(msg_err)

            # Permissions for '/root' should be set to 700
            # https://github.com/gardenlinux/gardenlinux/issues/813
            perm_root = utils.get_file_perm(client, '/root')
            perm_root_allow = 700
            if perm_root != perm_root_allow:
                msg_err = f"Directory /root is not set to {perm_root_allow}"
                logger.error(msg_err)
                raise TestFailed(msg_err)

        return cls.instance
