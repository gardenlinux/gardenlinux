from helper.exception import NotPartOfFeatureError, DisabledBy
from helper.tests.capabilities import Capabilities
import pytest

def test_capabilities(client, features):
    """The test function executed by pytest"""
    try:
        Capabilities(client, features)
    except (NotPartOfFeatureError, DisabledBy) as e:
        pytest.skip(str(e))