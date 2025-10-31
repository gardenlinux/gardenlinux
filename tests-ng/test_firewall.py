import pytest
from plugins.nft import Nft


@pytest.mark.root(reason="nft is only accessible by root")
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
    assert len(matching_policies) == 1, f"input has policy drop not as default"
