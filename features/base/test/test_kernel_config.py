from helper.exception import NotPartOfFeatureError, DisabledBy
from helper.tests.kernel_config import KernelConfig
import pytest

def test_kernel_config(client, features):
    """The test function executed by pytest"""
    try:
        KernelConfig(client, features)
    except (NotPartOfFeatureError, DisabledBy) as e:
        pytest.skip(str(e))