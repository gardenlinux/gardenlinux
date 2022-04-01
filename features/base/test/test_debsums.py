from helper.exception import NotPartOfFeatureError, DisabledBy
from helper.tests.debsums import Debsums
import pytest

def test_debsums(client, features):
    """The test function executed by pytest"""
    try:
        Debsums(client, features)
    except (NotPartOfFeatureError, DisabledBy) as e:
        pytest.skip(str(e))