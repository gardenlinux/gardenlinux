import pytest
from plugins.file import File

# =============================================================================
# _fwcfg Feature
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-_fwcfg-script-run-qemu-fw_cfg-script"])
@pytest.mark.feature("_fwcfg")
def test_fwcfg_run_script_exists(file: File):
    """Test that qemu-fw_cfg run script exists"""
    assert file.is_regular_file("/usr/bin/run-qemu-fw_cfg-script")


# =============================================================================
# kvm Feature
# =============================================================================


@pytest.mark.testcov(
    [
        "GL-TESTCOV-kvm-config-udev-rules-onmetal",
    ]
)
@pytest.mark.feature("kvm")
def test_kvm_udev_rules_onmetal_exists(file: File):
    """Test that KVM udev rules for OnMetal exist"""
    assert file.exists(
        "/etc/udev/rules.d/60-onmetal.rules"
    ), "KVM OnMetal udev rules should exist"
