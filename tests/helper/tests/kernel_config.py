import logging
import re

from helper import utils
from helper.exception import NotPartOfFeatureError, TestFailed, DisabledBy

logger = logging.getLogger(__name__)


class KernelConfig():
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
        test_is_disabled = utils.disabled_by(enabled_features, 'kernel-config')
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
            cls.instance = super(KernelConfig, cls).__new__(cls)

            (exit_code, output, error) = client.execute_command(
                "cat /boot/config-*", quiet=True)
            assert exit_code == 0, f"no {error=} expected"

            expected_config = utils.read_test_config(
                enabled_features, 'kernel-config', '.txt',
                filter_comments = False)

            config_dict = cls._to_dict(cls.instance, output)
            expected_config_dict = cls._to_dict(cls.instance, expected_config)

            logger.info(expected_config_dict)
            not_matching = []
            for key, value in expected_config_dict.items():
                if key in config_dict:
                    if (value == "n" or value == "is not set") and \
                       (config_dict[key] == "n" or \
                        config_dict[key] == "is not set"):
                        continue
                    if not config_dict[key] == value:
                        not_matching.append(key)

            if not len(not_matching) == 0:
                cls.failed_before = True
                raise TestFailed(
                    f"the following kernel config parameters do not match: " +
                    f"{', '.join(not_matching)}")
            
        return cls.instance

    def _to_dict(self, input):
        """convert input into a dictionary where the first entry of a line is
        used as key, remove everything that is not a CONFIG_ parameter"""
        input_list = []
        if not type(input) == list:
            for line in input.splitlines():
                input_list.append(line)
        else:
            input_list = input
        output = {}
        for entry in input_list:
            if not re.match(r".*CONFIG_", entry):
                continue
            entry = re.sub("^# *", "", entry)
            entry = entry.replace("=", " ")
            entry_as_list = entry.split(" ", 1)
            output.update({entry_as_list[0] : entry_as_list[1]})
        return output
