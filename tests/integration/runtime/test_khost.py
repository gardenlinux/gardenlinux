import pytest
from plugins.file import File

# =============================================================================
# khost Feature - Kubernetes Host Extended
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-khost-config-security-no-apparmor-init",
    ]
)
@pytest.mark.feature("khost")
def test_khost_no_apparmor_init(file: File):
    """Test that khost does not have AppArmor init script"""
    assert not file.exists(
        "/etc/init.d/apparmor"
    ), "Kubernetes host should not have AppArmor init script"
