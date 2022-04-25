from helper.exception import NotPartOfFeatureError, DisabledBy
from helper.tests.debian_cis import DebianCIS
import pytest

def test_feature_debian_cis(client, features, non_chroot):
    """The test function executed by pytest"""
    try:
        DebianCIS(client, features)
    except (NotPartOfFeatureError, DisabledBy) as e:
        pytest.skip(str(e))
