from pathlib import Path
import pytest

from plugins.capabilities import Capabilities

# There are two debian packages that provide an 'arping' binary
# https://packages.debian.org/search?searchon=contents&keywords=arping&mode=path&suite=stable&arch=any
# /usr/bin/arping is provided by iputils-arping
# /usr/sbin/arping is provided by arping
# We only use iputils-arping
expected_capabilities_by_feature = {
    "kvm": ["/usr/bin/arping cap_net_raw=ep"],
    "vmware": ["/usr/bin/arping cap_net_raw=ep"],
    "capi": ["/usr/bin/arping cap_net_raw=ep"],
    "_pxe": ["/usr/bin/arping cap_net_raw=ep"],
}


@pytest.mark.root(reason="Need to read files not readably by unprivileged user")
def test_only_expected_capabilities_are_set(
    active_features, capabilities: Capabilities
):
    expected_capabilities = set(
        [
            capability
            for feature in active_features
            for capability in expected_capabilities_by_feature.get(feature, [])
        ]
    )

    actual_capabilities = set(capabilities.list())

    assert (
        actual_capabilities == expected_capabilities
    ), f"Expected this list of capabilities {expected_capabilities} but got {actual_capabilities}"
