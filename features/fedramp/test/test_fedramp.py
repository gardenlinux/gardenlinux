from helper.tests.fedramp import fedramp
import pytest

# Parametrize the test unit
# with further options.
@pytest.mark.parametrize(
     "tests",
     [ 
         "/gardenlinux/features/fedramp/test/test.sh"
     ] 
 )

# Skip the test unit when the corresponding
# feature is not enabled in artifact.
#@pytest.mark.skip_feature_if_not_enabled()

# Run the test unit to perform the
# final tests by the given artifact.
def test_fedramp(client, tests):
    fedramp(client, tests)
