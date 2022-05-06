from helper.exception import NotPartOfFeatureError, DisabledBy
from helper.tests.sgid_suid import SGIDSUID
import pytest

def test_sgid_suid(client, features):
    """The test function executed by pytest"""
    try:
        SGIDSUID(client, features)
    except (NotPartOfFeatureError, DisabledBy) as e:
        pytest.skip(str(e))
