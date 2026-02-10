import pytest
from plugins.file import File

# =============================================================================
# _usi Feature
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-_usi-config-kernel-cmdline-no-gpt-auto"
        "GL-SET-_usi-config-update-motd-secureboot"
        "GL-SET-_usi-config-script-update-kernel-cmdline"
        "GL-SET-_usi-config-script-enroll-gardenlinux-secureboot-keys"
    ]
)
@pytest.mark.feature("_usi")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test__usi_files(file: File):
    """Test that files are present in initrd"""
    paths = [
        "/etc/kernel/cmdline.d/99-no-gpt-auto.cfg",
        "/etc/update-motd.d/25-secureboot",
        "/usr/local/sbin/update-kernel-cmdline",
        "/usr/sbin/enroll-gardenlinux-secureboot-keys",
    ]

    missing = [path for path in paths if not file.exists(path)]
    assert not missing, f"The following files were not found: {', '.join(missing)}"
