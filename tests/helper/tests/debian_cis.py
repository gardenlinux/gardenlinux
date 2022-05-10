import logging
import yaml
import os

from helper import utils
from helper.exception import NotPartOfFeatureError, TestFailed, DisabledBy

logger = logging.getLogger(__name__)


class DebianCIS():
    """Class containing the test for validating CIS compliance by OVH"""
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
            cls.instance = super(DebianCIS, cls).__new__(cls)

            config_file = f"/gardenlinux/features/{my_feature}/test/config.yaml"
            if os.path.exists(config_file):
                with open(config_file) as f:
                    feature_config = yaml.safe_load(f)
            else:
                msg_err = f"config for feature {my_feature} is not present."
                logger.error(msg_err)
                pytest.exit(msg_err, 1)

            # Redefine VARs from YAML (shortener)
            git_debian_cis = feature_config[my_feature]["git_debian_cis"]
            git_debian_cis =  feature_config[my_feature]["git_debian_cis"]
            git_gardenlinux = feature_config[my_feature]["git_gardenlinux"]
            config_src = feature_config[my_feature]["config_src"]
            config_dst = feature_config[my_feature]["config_dst"]
            script_src = feature_config[my_feature]["script_src"]
            script_dst = feature_config[my_feature]["script_dst"]

            # /tmp has 'noexec' flag; therefore we need to
            # call each script with bash.
            cmd_debian_cis = "for i in `ls /tmp/debian-cis/bin/hardening/*.sh`; do /bin/bash $i; done"

            (exit_code, output, error) = client.execute_command(f"cd /tmp/ && git clone {git_debian_cis}")
            assert exit_code == 0, f"no {error=} expected"

            (exit_code, output, error) = client.execute_command(f"cd /tmp/ && git clone {git_gardenlinux}")
            assert exit_code == 0, f"no {error=} expected"

            (exit_code, output, error) = client.execute_command("echo CIS_ROOT_DIR='/tmp/debian-cis' > /etc/default/cis-hardening")
            assert exit_code == 0, f"no {error=} expected"

            (exit_code, output, error) = client.execute_command(f"cp {config_src} {config_dst}")
            assert exit_code == 0, f"no {error=} expected"


            (exit_code, output, error) = client.execute_command(f"cp {script_src} {script_dst}")
            assert exit_code == 0, f"no {error=} expected"

            (exit_code, output, error) = client.execute_command(f"{cmd_debian_cis}")
            if "Check Failed" in output:
                exit_code == 1
                assert output
            assert exit_code == 0, f"no {error=} expected"

        return cls.instance
