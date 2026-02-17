import pytest
from plugins.file import File

# =============================================================================
# _iso Feature - ISO Installation Scripts
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-_iso-script-install-fstab",
    ]
)
@pytest.mark.feature("_iso")
def test_iso_install_fstab_script(file: File):
    """Test that ISO has install fstab script"""
    assert file.exists(
        "/opt/install/install.fstab"
    ), "ISO install fstab script should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-_iso-script-install-part",
    ]
)
@pytest.mark.feature("_iso")
def test_iso_install_partition_script(file: File):
    """Test that ISO has install partition script"""
    assert file.exists(
        "/opt/install/install.part"
    ), "ISO install partition script should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-_iso-script-install-sh",
    ]
)
@pytest.mark.feature("_iso")
def test_iso_install_main_script(file: File):
    """Test that ISO has main install script"""
    assert file.exists(
        "/opt/install/install.sh"
    ), "ISO main install script should exist"
