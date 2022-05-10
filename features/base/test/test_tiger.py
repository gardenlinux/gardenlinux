from helper.exception import NotPartOfFeatureError, DisabledBy
from helper.tests.tiger import Tiger
import pytest

def test_tiger(client, features, chroot):
    """The test function executed by pytest"""
    try:
        Tiger(client, features)
    except (NotPartOfFeatureError, DisabledBy) as e:
        pytest.skip(str(e))