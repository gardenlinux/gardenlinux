from helper.tests.machine_id import machine_id
import pytest

@pytest.mark.skip_feature()
def test_machine_id(client):
    machine_id(client)
