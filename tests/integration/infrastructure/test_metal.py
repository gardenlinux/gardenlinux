from re import A

import pytest
from plugins.file import File
from plugins.parse_file import ParseFile

# =============================================================================
# metal Feature - Bare Metal Configuration
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-cloud-config-kernel-entry-token",
        "GL-SET-metal-config-kernel-entry-token",
    ]
)
@pytest.mark.feature("cloud or metal")
def test_kernel_entry_token_exists(file: File):
    """Test that cloud or metal has kernel entry token"""
    assert file.exists("/etc/kernel/entry-token"), "Kernel entry token should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-cloud-config-kernel-entry-token",
        "GL-SET-metal-config-kernel-entry-token",
    ]
)
@pytest.mark.feature("cloud or metal")
def test_kernel_entry_token_content(parse_file: ParseFile):
    """Test that cloud or metal has kernel entry token"""
    config = parse_file.lines("/etc/kernel/entry-token")
    assert "Default" in config, "Kernel entry token should be Default"


@pytest.mark.setting_ids(
    [
        "GL-SET-metal-config-kernel-postinst-cmdline",
    ]
)
@pytest.mark.feature("metal")
def test_metal_kernel_postinst_cmdline(file: File):
    """Test that metal has kernel postinst cmdline script"""
    assert file.exists(
        "/etc/kernel/postinst.d/00-kernel-cmdline"
    ), "Metal kernel postinst cmdline script should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-metal-config-kernel-postinst-ucode",
    ]
)
@pytest.mark.feature("metal")
def test_metal_kernel_postinst_ucode(file: File):
    """Test that metal has kernel postinst microcode script"""
    assert file.exists(
        "/etc/kernel/postinst.d/00-ucode"
    ), "Metal kernel postinst ucode script should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-metal-config-kernel-postinst-update-syslinux",
    ]
)
@pytest.mark.feature("metal")
def test_metal_kernel_postinst_syslinux(file: File):
    """Test that metal has kernel postinst syslinux update script"""
    assert file.exists(
        "/etc/kernel/postinst.d/zz-update-syslinux"
    ), "Metal kernel postinst syslinux script should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-metal-config-kernel-postrm-update-syslinux",
    ]
)
@pytest.mark.feature("metal")
def test_metal_kernel_postrm_syslinux(file: File):
    """Test that metal has kernel postrm syslinux update script"""
    assert file.exists(
        "/etc/kernel/postrm.d/zz-update-syslinux"
    ), "Metal kernel postrm syslinux script should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-metal-config-no-init-ipmievd",
        "GL-SET-metal-config-no-init-irqbalance",
        "GL-SET-metal-config-no-mdadm",
        "GL-SET-metal-config-no-network",
        "GL-SET-metal-config-no-runit-001",
        "GL-SET-metal-config-no-runit-002",
        "GL-SET-metal-config-no-sv",
    ]
)
@pytest.mark.feature("metal")
def test_metal_removed_files(file: File):
    """Test that metal does not have removed files"""
    removed_files = [
        "/etc/init.d/ipmievd",
        "/etc/init.d/irqbalance",
        "/etc/mdadm.conf",
        "/etc/mdadm/mdadm.conf",
        "/etc/network/interfaces",
        "/etc/runit",
        "/etc/sv",
    ]
    missing = [file_path for file_path in removed_files if file.exists(file_path)]
    assert not missing, f"Metal removed files should not exist: {', '.join(missing)}"


@pytest.mark.setting_ids(
    [
        "GL-SET-metal-config-udev-rules-intellldp",
    ]
)
@pytest.mark.feature("metal")
def test_metal_udev_rules_intellldp(file: File):
    """Test that metal has Intel LDP udev rules"""
    assert file.exists(
        "/etc/udev/rules.d/71-intellldp.rules"
    ), "Metal Intel LDP udev rules should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-metal-config-udev-rules-nostbyrot",
    ]
)
@pytest.mark.feature("metal")
def test_metal_udev_rules_nostbyrot(file: File):
    """Test that metal has no standby rotation udev rules"""
    assert file.exists(
        "/etc/udev/rules.d/69-nostbyrot.rules"
    ), "Metal nostbyrot udev rules should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-metal-script-update-usbids",
    ]
)
@pytest.mark.feature("metal")
def test_metal_update_usbids_script(file: File):
    """Test that metal has update-usbids script"""
    assert file.exists(
        "/usr/sbin/update-usbids"
    ), "Metal update-usbids script should exist"
