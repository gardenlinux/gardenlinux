from helper.exception import NotPartOfFeatureError, DisabledBy
from helper.tests.debian_cis import DebianCIS
import pytest

def test_feature_cis_lynis(client, features):
    """The test function executed by pytest"""
    try:
        DebianCIS(client, features)
    except (NotPartOfFeatureError, DisabledBy) as e:
        pytest.skip(str(e))
