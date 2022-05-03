from helper.exception import NotPartOfFeatureError, DisabledBy
from helper.tests.find_dup_uids import FindDupUIDs 
import pytest

def test_duplicate_uids(client, features):
    """The test function executed by pytest"""
    try:
        FindDupUIDs(client, features)
    except (NotPartOfFeatureError, DisabledBy) as e:
        pytest.skip(str(e))
