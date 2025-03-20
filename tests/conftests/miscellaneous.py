"""miscellaneous for the conftest"""

import pytest

@pytest.fixture
def non_feature_githubActionRunner(testconfig):
    """
    Some of the tests won't execute susccessul on the github runner.
    With this we can skip running them on Github Actions.
    """
    features = testconfig.get("features", [])
    if "githubActionRunner" in features:
        pytest.skip('test is not supported on githubActionRunner')
