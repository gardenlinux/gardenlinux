import pytest
from helper.sshclient import RemoteClient


def test_metadata_connection(client, non_gcp, non_azure, non_ali, non_chroot, non_kvm):
    metadata_host = "169.254.169.254"
    # request the IMDSv2 token to allow access to the metadata_host on AWS.
    (exit_code, token, error) = client.execute_command(
            f"curl -sqX PUT 'http://{metadata_host}/latest/api/token'\
                    -H 'X-aws-ec2-metadata-token-ttl-seconds:60'"
    )
    (exit_code, output, error) = client.execute_command(
        f"wget --timeout 5 \
               --header='X-aws-ec2-metadata-token: {token}' \
               'http://{metadata_host}/'"
    )
    assert exit_code == 0, f"no {error=} expected"
    assert f"Connecting to {metadata_host}:80... connected." in error
    assert "200 OK" in error


def test_metadata_connection_azure(client, azure):
    metadata_url = "http://169.254.169.254/metadata/instance/compute?api-version=2021-01-01&format=json"
    (exit_code, output, error) = client.execute_command(
        f"curl --connect-timeout 5 '{metadata_url}' -H 'Metadata: true'"
    )
    assert exit_code == 0, f"no {error=} expected"


def test_metadate_connection_aliyun(client, ali):
    metadata_url = "http://100.100.100.200/2016-01-01"
    (exit_code, output, error) = client.execute_command(
        f"curl --connect-timeout 5 '{metadata_url}' -H 'Metadata: true'"
    )
    assert exit_code == 0, f"no {error=} expected"
