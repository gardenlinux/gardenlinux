from helper.exception import NotPartOfFeatureError, DisabledBy
from helper.tests.ssh_authorized import SshAuthorized
import pytest

def test_ssh_authorized(client, features, testconfig):
    """The test function executed by pytest"""
    try:
        SshAuthorized(client, features, testconfig)
    except (NotPartOfFeatureError, DisabledBy) as e:
        pytest.skip(str(e))
