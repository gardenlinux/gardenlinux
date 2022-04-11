import logging

from helper import utils
from helper.exception import NotPartOfFeatureError, TestFailed, DisabledBy

logger = logging.getLogger(__name__)


class CISLynis():
    """Class containing the test for validating CIS compliance by Lynis"""
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
        test_is_disabled = utils.disabled_by(enabled_features, 'cis')
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
            cls.instance = super(CISLynis, cls).__new__(cls)


            lynis_version   = "3.0.7"
            lynis_binary    = f"https://downloads.cisofy.com/lynis/lynis-{lynis_version}.tar.gz"
            lynis_report    = "/var/log/lynis-report.dat"
            lynis_gl_branch = "main"
            lynis_config = "https://raw.githubusercontent.com/gardenlinux/gardenlinux/feature/add-unit-test-cis/features/cis/test/custom.prf"

            (exit_code, output, error) = client.execute_command(f"wget -O /tmp/lynis.tar.gz {lynis_binary}")
            assert exit_code == 0, f"no {error=} expected"

            (exit_code, output, error) = client.execute_command("tar xfvz /tmp/lynis.tar.gz -C /tmp/")
            assert exit_code == 0, f"no {error=} expected"

            (exit_code, output, error) = client.execute_command(f"wget -O /tmp/lynis/custom.prf {lynis_config}")
            assert exit_code == 0, f"no {error=} expected"

            # Unfortunately we need to change to the
            # lynis dir before we may execute lynis
            (exit_code, output, error) = client.execute_command("cd /tmp/lynis/ && /usr/bin/sh /tmp/lynis/lynis --no-log audit system > /tmp/lynis.output")
            assert exit_code == 0, f"no {error=} expected"

            (exit_code, output, error) = client.execute_command("cat /tmp/lynis.output")
            validation = False
            if "Great, no warnings" in output:
                validation = True
            assert validation

            (exit_code, output, error) = client.execute_command(f"cat {lynis_report}")
            validation = False
            if not "warning[]" in output:
                validation = True
            assert validation

            (exit_code, output, error) = client.execute_command(f"cat {lynis_report}")
            validation = False
            if not "critical[]" in output:
                validation = True
            assert validation

        return cls.instance
