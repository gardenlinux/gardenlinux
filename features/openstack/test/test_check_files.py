from helper.utils import check_file
import pytest


@pytest.mark.parametrize(
    "file_name",
    [
        "/etc/cloud/ds-identify.cfg",
        "/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg",
        "/etc/cloud/cloud.cfg.d/50-datasource.cfg",
        "/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg"
    ]
)


def test_check_file(client, file_name):
    exists = check_file(client, file_name)
    assert exists, f"File {file_name} could not be found."
