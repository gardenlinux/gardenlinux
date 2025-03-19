from helper.utils import execute_remote_command


def test_nft_config(client, non_provisioner_chroot):
    # This will already fail if table "inet" is missing
    out = execute_remote_command(client, "nft list table inet filter")
    # Validate that input has policy drop as default
    assert "type filter hook input priority filter; policy drop;" in out
