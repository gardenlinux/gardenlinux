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

        # Check if dmesg_restrict is explicitly enabled in config
        (exit_code, output, error) = client.execute_command(
            f"grep -qr 'kernel.dmesg_restrict = 1' /etc/sysctl.conf /etc/sysctl.d/*.conf",
            quiet=True)

        assert exit_code == 0, \
            f"Expected kernel.dmesg_restrict to be enabled"

        # Check if dmesg_restrict is explicitly disabled in config
        (exit_code, output, error) = client.execute_command(
            f"grep -qr 'kernel.dmesg_restrict = 0' /etc/sysctl.conf /etc/sysctl.d/*.conf",
            quiet=True)

        assert exit_code == 1, \
            f"Unexpectedly detected kernel.dmesg_restrict to be disabled"

        # Check if dmesg_restrict is enabled
        (exit_code, output, error) = client.execute_command(
            f"sysctl kernel.dmesg_restrict",
            quiet=True)

        assert output == 'kernel.dmesg_restrict = 1',\
            f"sysctl kernel.dmesg_restrict returned unexpected output"

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
