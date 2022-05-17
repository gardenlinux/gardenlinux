from helper.tests.capabilities import capabilities
import pytest

@pytest.mark.parametrize(
    "capability_list",
    [
        [
            "/usr/bin/arping cap_net_raw=ep",
            "/usr/bin/ping cap_net_raw=ep"
        ]
    ]
)
def test_capabilities(client, capability_list):
    capabilities(client, capability_list)