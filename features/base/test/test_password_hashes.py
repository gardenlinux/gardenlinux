from helper.exception import NotPartOfFeatureError, DisabledBy
from helper.tests.password_hashes import PasswordHashes
import pytest

def test_password_hashes(client, features):
    """The test function executed by pytest"""
    try:
        PasswordHashes(client, features)
    except (NotPartOfFeatureError, DisabledBy) as e:
        pytest.skip(str(e))
