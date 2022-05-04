from helper.exception import NotPartOfFeatureError, DisabledBy
from helper.tests.dmesg_access import DmesgAccess
import pytest


def test_dmesg_access(client, features, non_chroot):
    """The test function executed by pytest"""
    try:
        DmesgAccess(client, features)
    except (NotPartOfFeatureError, DisabledBy) as e:
        pytest.skip(str(e))
