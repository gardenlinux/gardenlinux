import pytest
from plugins.file import File
from plugins.nft import Nft

# =============================================================================
# firewall Feature
# =============================================================================


@pytest.mark.testcov(
    [
        "GL-TESTCOV-firewall-config-nft-default",  # exact: tests nftables firewall configuration
    ]
)
@pytest.mark.root(reason="nft is only accessible by root")
@pytest.mark.booted(reason="Firewall needs booted system")
@pytest.mark.feature("firewall")
def test_nft_config(nft: Nft):
    matching_policies = [
        chain
        for chain in nft.list_table_inet_filter()
        if chain.type == "filter"
        and chain.hook == "input"
        and chain.prio == 0
        and chain.policy == "drop"
    ]
    assert len(matching_policies) == 1, "input has policy drop not as default"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-firewall-config-nftables-include",
    ]
)
@pytest.mark.feature("firewall")
def test_firewall_nft_default_config_exists(file: File):
    """Test that firewall nft default configuration exists"""
    assert file.exists(
        "/etc/nft.d/default.conf"
    ), "Firewall nft default configuration should exist"
