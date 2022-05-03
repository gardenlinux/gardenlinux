import logging

from helper import utils
from helper.exception import NotPartOfFeatureError, TestFailed, DisabledBy

logger = logging.getLogger(__name__)


class DmesgAccess():
    """Class containing test to verify non-root user has no access to dmesg"""
    failed_before = False

    def do_test_check_dmesg_access(cls, client):
        """Verifies that non-root users can NOT access dmesg"""
        cls.instance = super(DmesgAccess, cls).__new__(cls)
        message = "OK - dmesg restricted"
        rc = 1

        (exit_code, output, error) = client.execute_command(
            f"grep -q 'CONFIG_SECURITY_DMESG_RESTRICT=y' /boot/config-*",
            quiet=True)

        if exit_code == 0:
            message += "| kernel config parameter"
            rc = 0

        (exit_code, output, error) = client.execute_command(
            f"grep -qr 'kernel.dmesg_restrict = 1' /etc/sysctl*;",
            quiet=True)

        if exit_code == 0:
            message += "| sysctl parameter"
            rc = 0

        assert rc == 0,\
            f"FAIL - dmesg access for non-root users is not restricted"

        if rc == 0:
            logger.info(message)

    def __new__(cls, client, features):

        if cls.failed_before:
            raise Exception("This test failed before in another feature")

        (enabled_features, my_feature) = features

        test_is_disabled = utils.disabled_by(enabled_features, 'dmesg-access')
        if not len(test_is_disabled) == 0:
            raise DisabledBy("Test is explicitly disabled by features " +
                             f"{', '.join(test_is_disabled)}")

        if my_feature not in enabled_features:
            raise NotPartOfFeatureError(
                f"Feature {my_feature} this test belongs to is not enabled")

        if not hasattr(cls, 'instance'):
            cls.do_test_check_dmesg_access(cls, client)

        return cls.instance
