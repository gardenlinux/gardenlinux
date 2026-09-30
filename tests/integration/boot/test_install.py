import pytest
from plugins.file import File

# =============================================================================
# _install Feature - Installation Script
# =============================================================================


@pytest.mark.testcov(
    [
        "GL-TESTCOV-_install-script-install-sh",
    ]
)
@pytest.mark.feature("_install and not _autoinstall")
def test_install_script(file: File):
    """Test that main install script exists"""
    assert file.exists("/opt/install/install.sh"), "install script should exist"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-_install-config-repart-efi",
    ]
)
@pytest.mark.feature("_install and not _autoinstall")
def test_install_repart_efi_config(file: File):
    """Test that repart config for EFI exists"""
    assert file.exists(
        "/opt/install/repart/00-efi.conf"
    ), "repart config for EFI should exist"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-_install-config-repart-root",
    ]
)
@pytest.mark.feature("_install and not _autoinstall")
def test_install_repart_root_config(file: File):
    """Test that repart config for root exists"""
    assert file.exists(
        "/opt/install/repart/10-root.conf"
    ), "repart config for root should exist"
