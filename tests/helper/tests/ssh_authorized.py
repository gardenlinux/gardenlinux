import logging
import hashlib

from helper import utils
from helper.exception import NotPartOfFeatureError, TestFailed, DisabledBy

logger = logging.getLogger(__name__)


class SshAuthorized():
    """Class containing the test for checking if debsums are available"""
    failed_before = False
    def __new__(cls, client, features, config):
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
        test_is_disabled = utils.disabled_by(enabled_features, 'ssh_authorized')
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
            cls.instance = super(SshAuthorized, cls).__new__(cls)

            # get passwd
            (exit_code, output, error) = client.execute_command(
                "getent passwd", quiet=True)

            # check if users with login shell have authorized_keys file
            have_authorized_keys = []
            for line in output.split('\n'):
                if line != '' and not ("/bin/false" in line or 
                                    "nologin" in line or "/bin/sync" in line):
                    line = line.split(":")
                    home_dir = line[5]
                    user = line[0]
                    if _has_authorized_keys(client, home_dir):
                        have_authorized_keys.append(user)

            if len(have_authorized_keys) != 0:
                msg_err = (f"following users have authorized_keys defined " +
                            f"{' '.join(have_authorized_keys)}")
                logger.error(msg_err)
                raise TestFailed(msg_err)

            # check that the injected authorized_keys file is not modified
            ssh_key_path = config["ssh"]["ssh_key_filepath"]
            with open(f"{ssh_key_path}.pub", "rb") as authorized_keys_file:
                sha256_local = hashlib.sha256(
                                authorized_keys_file.read()).hexdigest()

            (exit_code, output, _) = client.execute_command(
                f"sha256sum /root/.ssh/test_authorized_keys", quiet=True)
            assert exit_code == 0, f"no {error=} expected"
            
            if sha256_local != output.split(' ', 1)[0]:
                msg_err = ("the authorized_keys file injected for testing " +
                            "was modified")
                logger.error(msg_err)
                raise TestFailed(msg_err)

        return cls.instance

def _has_authorized_keys(client, home_dir):
    files = ["authorized_keys", "authorized_keys2"]
    for file in files:
        (exit_code, _, _) = client.execute_command(
            f"ls {home_dir}/.ssh/{file}", quiet=True)
        if exit_code == 0:
            return True
    return False