import logging
import string

from helper import utils
from helper.exception import NotPartOfFeatureError, TestFailed, DisabledBy

logger = logging.getLogger(__name__)


class KernelParameter():
    """Class containing the test for checking kernel parameters."""
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
        test_is_disabled = utils.disabled_by(enabled_features,
                                                'kernel-parameter')
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
            cls.instance = super(KernelParameter, cls).__new__(cls)

            expected_parameters = utils.read_test_config(enabled_features,
                                                        "kernel-parameter")

            for parameter in expected_parameters:
                parameter = parameter.split('=')

                config_key = parameter[0].strip(string.whitespace)
                expected_value = parameter[1].strip(string.whitespace)

                (exit_code, output, error) = client.execute_command(
                    f"sysctl -n {config_key}", quiet=True)
                assert exit_code == 0, f"no {error=} expected"

                running_value = output.strip(string.whitespace)

                if running_value != expected_value:
                    cls.failed_before = True
                    msg_err = (f"{config_key.capitalize()} is not " +
                              f"configured correctly. Expected " +
                              f"{config_key} set to {expected_value}.")
                    logger.error(msg_err)
                    raise TestFailed(msg_err)
                    
        return cls.instance