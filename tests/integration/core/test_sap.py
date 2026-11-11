import pytest
from plugins.file import File


@pytest.mark.feature("sap")
@pytest.mark.testcov(["GL-TESTCOV-sap-config-shared-symlink"])
def test_shared_symlink(file: File):
    assert file.is_symlink(
        "/shared", target="/var/shared"
    ), "/shared must be a symlink pointing to /var/shared"
