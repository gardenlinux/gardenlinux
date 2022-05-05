from helper.exception import NotPartOfFeatureError, DisabledBy
from helper.tests.reset_env_vars import ResetEnvVars
import pytest

def test_reset_env_vars(client, features):
    """The test function executed by pytest"""
    try:
        ResetEnvVars(client, features)
    except (NotPartOfFeatureError, DisabledBy) as e:
        pytest.skip(str(e))