from helper.exception import NotPartOfFeatureError, DisabledBy
from helper.tests.packages_musthave import PackagesMusthave

import pytest

def test_packages_musthave(client, features):
    """The test function executed by pytest"""
    try:
        PackagesMusthave(client, features)
    except (NotPartOfFeatureError, DisabledBy) as e:
        pytest.skip(str(e))