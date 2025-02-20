"""
Features Flags.  
Please note: Feature flags must be prefixed with a "_", for example "_prod". 
"""

import pytest

@pytest.fixture
def non_dev(testconfig):
    features = testconfig.get("features", [])
    if "_dev" in features:
        pytest.skip('test not supported on dev feature')

@pytest.fixture
def non_trustedboot(testconfig):
    features = testconfig.get("features", [])
    if "_trustedboot" in features:
        pytest.skip('test not supported on trustedboot feature')

@pytest.fixture
def non_ephemeral(testconfig):
    features = testconfig.get("features", [])
    if "_ephemeral" in features:
        pytest.skip('test not supported on empemeral feature')

@pytest.fixture
def non_usi(testconfig):
    features = testconfig.get("features", [])
    usi = { '_trustedboot', '_ephemeral'}
    if usi in features:
        pytest.skip("test not supported on usi feature")
