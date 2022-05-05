from helper.exception import NotPartOfFeatureError, DisabledBy
from helper.tests.kernel_parameter import KernelParameter
import pytest

def test_kernel_parameter(client, features):
    """The test function executed by pytest"""
    try:
        KernelParameter(client, features)
    except (NotPartOfFeatureError, DisabledBy) as e:
        pytest.skip(str(e))