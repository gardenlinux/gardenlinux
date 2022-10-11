import pytest
from helper.sshclient import RemoteClient

def test_aws_ena_driver(client, aws):
    """ Test for network driver on aws platform """
    (exit_code, output, error) = client.execute_command("/sbin/ethtool -i $(ip -j link show  | jq -r '.[] | if .ifname != \"lo\" and .ifname != \"docker0\" then .ifname else empty end') | grep \"^driver\" | awk '{print $2}'")
    assert exit_code == 0, f"no {error=} expected"
    assert output.rstrip() == "ena", "Expected network interface to run with ena driver"
