from helper.exception import NotPartOfFeatureError, DisabledBy
from helper.tests.blacklisted_packages import BlacklistedPackages
import pytest

def test_blacklisted_packages(client, features):
    """The test function executed by pytest"""
    try:
        BlacklistedPackages(client, features)
    except (NotPartOfFeatureError, DisabledBy) as e:
        pytest.skip(str(e))