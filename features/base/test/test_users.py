from helper.exception import NotPartOfFeatureError, DisabledBy
from helper.tests.users import TestUsers
import pytest

def test_users(client, features):
    """The test function executed by pytest"""
    try:
        TestUsers(client, features)
    except (NotPartOfFeatureError, DisabledBy) as e:
        pytest.skip(str(e))
