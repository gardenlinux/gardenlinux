from helper.exception import NotPartOfFeatureError
from helper.tests.blacklisted_packages import BlacklistedPackages
import pytest

def test_blacklisted_packages(client, features):
    """The test function executed by pytest"""
    try:
        BlacklistedPackages(client, features)
    except NotPartOfFeatureError as e:
        pytest.skip(str(e))