from helper.tests.password_shadow import password_shadow
import pytest


@pytest.mark.security_id(168)
@pytest.mark.security_id(170)
def test_password_shadow(client):
    password_shadow(client)
