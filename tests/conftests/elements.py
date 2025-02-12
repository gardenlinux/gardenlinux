"""
Features Elements.
"""

import pytest


@pytest.fixture
def non_vhost(testconfig):
    features = testconfig.get("features", [])
    if "vhost" in features:
        pytest.skip('test not supported with vhost feature enabled')

@pytest.fixture
def non_feature_gardener(testconfig):
    features = testconfig.get("features", [])
    if "gardener" in features:
        pytest.skip('test is not supported on gardener')
