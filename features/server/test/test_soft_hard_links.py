from helper.exception import NotPartOfFeatureError, DisabledBy
from helper.tests.soft_hard_links import SoftHardLinks
import pytest

def test_soft_hard_links(client, features):
    """The test function executed by pytest"""
    try:
        SoftHardLinks(client, features)
    except (NotPartOfFeatureError, DisabledBy) as e:
        pytest.skip(str(e))