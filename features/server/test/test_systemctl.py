from helper.exception import NotPartOfFeatureError, DisabledBy
from helper.tests.systemctl import Systemctl
import pytest

def test_systemctl(client, features):
    """The test function executed by pytest"""
    try:
        Systemctl(client, features)
    except (NotPartOfFeatureError, DisabledBy) as e:
        pytest.skip(str(e))