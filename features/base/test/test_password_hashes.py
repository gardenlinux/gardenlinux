from helper.tests.password_hashes import password_hashes 
import pytest 


@pytest.mark.security_id(325)
def test_password_hashes(client):
    password_hashes(client)
