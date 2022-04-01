from helper.exception import NotPartOfFeatureError
from helper.tests.capabilities import Capabilities
import pytest

def test_capabilities(client, features):
    """The test function executed by pytest"""
    try:
        Capabilities(client, features)
    except NotPartOfFeatureError as e:
        pytest.skip(str(e))