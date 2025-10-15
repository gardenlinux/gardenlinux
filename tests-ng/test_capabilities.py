from pathlib import Path
import pytest

from plugins.capabilities import Capabilities

# There are two debian packages that provide an 'arping' binary
# https://packages.debian.org/search?searchon=contents&keywords=arping&mode=path&suite=stable&arch=any
# /usr/bin/arping is provided by iputils-arping
# /usr/sbin/arping is provided by arping
# We only use iputils-arping
capabilities_allowlist = set(["/usr/bin/arping cap_net_raw=ep"])


@pytest.mark.root(reason="Need to read files not readable by unprivileged user")
def test_only_expected_capabilities_are_set(
    capabilities: Capabilities
):

    actual_capabilities = set(capabilities.list())

    assert (
        actual_capabilities - capabilities_allowlist == set()
    ), f"Cannot have more capabilities than {capabilities_allowlist} but got {actual_capabilities}"
