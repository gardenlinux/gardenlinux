import logging

from helper import utils
from helper.exception import NotPartOfFeatureError, TestFailed, DisabledBy

logger = logging.getLogger(__name__)


class Systemctl():
    """Class containing the test for blacklisted packages"""
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
        test_is_disabled = utils.disabled_by(
            enabled_features, 'systemctl')
        if not len(test_is_disabled) == 0:
            raise DisabledBy(
                "Test is explicitly disabled by features " +
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
            cls.instance = super(Systemctl, cls).__new__(cls)

            # get list of enabled system services
            (exit_code, output, error) = client.execute_command(
                "systemctl list-unit-files | awk '$2~/static/ { print $1; " +
                "next} $2~/enabled/ { print $1; next; }'", quiet=True)
            assert exit_code == 0, f"no {error=} expected"
            enabled = output

            # get list of disabled system services
            (exit_code, output, error) = client.execute_command(
                "systemctl list-unit-files | awk '$2~/disabled/ { print $1; " +
                "next}'", quiet=True)
            assert exit_code == 0, f"no {error=} expected"
            disabled = output

            expected_enabled = utils.read_test_config(
                enabled_features, 'systemctl', '_enabled.list')

            expected_disabled = utils.read_test_config(
                enabled_features, 'systemctl', '_disabled.list')

            missing_enabled = _check_missing(enabled, expected_enabled)
            missing_disabled = _check_missing(disabled, expected_disabled)

            if not len(missing_enabled) == 0:
                cls.failed_before = True
                raise TestFailed(f"{', '.join(missing_enabled)} are " +
                    "not enabled as expected")
            
            if not len(missing_disabled) == 0:
                cls.failed_before = True
                raise TestFailed(f"{', '.join(missing_disabled)} are " +
                    "not disabled as expected")

        return cls.instance

def _check_missing(configured, expected):
    """Check if an item of the expected list is in configured, returns a list
    containing the items not found"""
    missing = []
    for item in expected:
        if not item in configured:
            missing.append(item)
    return missing
