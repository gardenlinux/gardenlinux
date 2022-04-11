from helper.exception import NotPartOfFeatureError, DisabledBy
from helper.tests.cis_lynis import CISLynis
import pytest

def test_feature_cis_lynis(client, features):
    """The test function executed by pytest"""
    try:
        CISLynis(client, features)
    except (NotPartOfFeatureError, DisabledBy) as e:
        pytest.skip(str(e))
