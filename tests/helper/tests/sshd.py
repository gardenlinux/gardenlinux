import logging
import re

from helper import utils
from helper.exception import NotPartOfFeatureError, TestFailed, DisabledBy

logger = logging.getLogger(__name__)


class Sshd():
    """Class containing the test for blacklisted packages"""

    IN_SSHD_CONFIG = 1
    NOT_IN_SSHD_CONFIG = 2
    DIFFERENT = 3

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
            enabled_features, 'blacklisted_packages')
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
            cls.instance = super(Sshd, cls).__new__(cls)

            (exit_code, output, error) = client.execute_command("sshd -T",
                                                                quiet=True)
            assert exit_code == 0, f"no {error=} expected"

            sshd_config = cls._create_dict(cls.instance, output)

            expected = utils.read_test_config(
                enabled_features, 'sshd', '_expected')
            sshd_expected = cls._create_dict(cls.instance, expected)

            for key, value in sshd_config.items():
                if key in sshd_expected:
                    sshd_config_value = cls._normalize_value(
                                            cls.instance, value)
                    expected_value = cls._normalize_value(
                                        cls.instance, sshd_expected[key])
                    missing, where = cls._compare_as_set(cls.instance,
                                        sshd_config_value, expected_value)
                    if where == cls.NOT_IN_SSHD_CONFIG:
                        cls.failed_before = True
                        raise TestFailed(f"For {key} '{', '.join(missing)}'" +
                            " is expected but missing")
                    if where == cls.IN_SSHD_CONFIG:
                        cls.failed_before = True
                        raise TestFailed(f"For {key} '{', '.join(missing)}'" +
                            " is set but not expected")
                    if where == cls.DIFFERENT:
                        cls.failed_before = True
                        raise TestFailed(f"For {key} " +
                            f"'{', '.join(expected_value)}' is expected, " +
                            f"'{', '.join(sshd_config_value)}' is set")

        return cls.instance

    def _create_dict(self, input):
        """Create a dictionary.
        Expecting a list or newline seperated input. The first word of a line
        or list element will become the key, the rest is the value, the value 
        is returned as a list"""
        out = {}
        if type(input) == list:
            for line in input:
                l = line.split(' ')
                out.update({l[0].lower(): l[1:]})
        else:
            for line in input.splitlines():
                l = line.split(' ')
                out.update({l[0].lower(): l[1:]})
        return out

    def _normalize_value(self, list):
        """Convert a given list.
        All elements will be converted to lower case and the list will be
        returned as a set. If the element contains a comma separated string,
        it will be split into a list first."""
        normalized = []
        for item in list:
            normalized.append(item.lower())
        if len(normalized) == 1 and re.match(r".*,.*",normalized[0]):
            value_as_set = set(normalized[0].split(','))
        else:
            value_as_set = set(normalized)
        return value_as_set

    def _compare_as_set(self, sshd_config_value, expected_value):
        """Compare 2 sets.
        If the sets are not identical, return the difference between the sets
        and in which set the difference is missing"""
        if not (sshd_config_value.issuperset(expected_value) and
                expected_value.issuperset(sshd_config_value)):
            missing_value = sshd_config_value.symmetric_difference(
                                expected_value)
            if sshd_config_value.issubset(expected_value):
                return missing_value, self.NOT_IN_SSHD_CONFIG
            if expected_value.issubset(sshd_config_value):
                return missing_value, self.IN_SSHD_CONFIG
            else:
                return missing_value, self.DIFFERENT
        else:
            return None, 0
