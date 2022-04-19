from helper.exception import NotPartOfFeatureError, DisabledBy
from helper.tests.sshd import Sshd
import pytest

def test_sshd(client, features):
    """The test function executed by pytest"""
    try:
        Sshd(client, features)
    except (NotPartOfFeatureError, DisabledBy) as e:
        pytest.skip(str(e))