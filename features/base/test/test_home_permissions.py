from helper.exception import NotPartOfFeatureError, DisabledBy
from helper.tests.home_permissions import HomePermissions
import pytest

def test_home_permissions(client, features):
    """The test function executed by pytest"""
    try:
        HomePermissions(client, features)
    except (NotPartOfFeatureError, DisabledBy) as e:
        pytest.skip(str(e))
