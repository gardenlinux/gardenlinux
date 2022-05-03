import logging
import os

from helper import utils
from helper.exception import NotPartOfFeatureError, TestFailed, DisabledBy

logger = logging.getLogger(__name__)


class Tiger():
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
        test_is_disabled = utils.disabled_by(enabled_features, 'tiger')
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
            cls.instance = super(Tiger, cls).__new__(cls)

            utils.AptUpdate(client)                
            (exit_code, output, error) = client.execute_command(
                "apt-get install -y --no-install-recommends tiger apt-utils",
                quiet=True)
            assert exit_code == 0, f"no {error=} expected"

            # merge tiger config files for enabled features
            with open("/tmp/tigerrc", "w") as merged_config:
                for feature in enabled_features:
                    path = (f"/gardenlinux/features/{feature}" + 
                            "/test/tiger.d/tigerrc")
                    if os.path.isfile(path):
                        with open(path) as feature_config:
                            merged_config.write(feature_config.read())

            # upload tiger config file
            client.remote_path = "/tmp"
            client.bulk_upload(["/tmp/tigerrc"])

            # unmount directories that make the tiger checks fail
            for dir in ["sys", "dev", "proc"]:
                (exit_code, output, error) = client.execute_command(
                    f"mountpoint -q /{dir} && umount -l /{dir}", quiet=True)
                assert exit_code == 0, f"no {error=} expected"

            (exit_code, output, error) = client.execute_command(
                "tiger -c /tmp/tigerrc -q", quiet=True)
            assert exit_code == 0, f"no {error=} expected"

            (exit_code, output, error) = client.execute_command(
                "grep -hw FAIL /var/log/tiger/security.report.*", quiet=True)
            if not output == '':
                cls.failed_before = True
                raise TestFailed(
                    f"tiger detected the following errors: {output}")

        return cls.instance