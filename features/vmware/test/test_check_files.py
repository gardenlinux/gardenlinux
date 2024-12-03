from helper.utils import check_file
import pytest


@pytest.mark.parametrize(
    "file_name",
    [
        "/usr/bin/dscheck_VMwareGuestInfo",
        "/usr/lib/python3/dist-packages/cloudinit/sources/DataSourceVMwareGuestInfo.py",
        "/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg",
        "/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg",
        "/etc/cloud/cloud.cfg.d/99_enabled-datasources.cfg"
    ]
)


def test_check_file(client, file_name):
    exists = check_file(client, file_name)
    assert exists, f"File {file_name} could not be found."
