from helper.exception import NotPartOfFeatureError, DisabledBy
from helper.tests.password_shadow import PasswordShadow
import pytest

def test_password_shadow(client, features):
    """The test function executed by pytest"""
    try:
        PasswordShadow(client, features)
    except (NotPartOfFeatureError, DisabledBy) as e:
        pytest.skip(str(e))
