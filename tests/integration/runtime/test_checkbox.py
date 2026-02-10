from math import e
from mimetypes import init
from typing import List

import pytest
from plugins.file import File
from plugins.parse_file import ParseFile

# =============================================================================
# checkbox Feature - Hardware Testing Framework
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-checkbox-config-checkbox-test-plan",
    ]
)
@pytest.mark.feature("checkbox")
def test_checkbox_test_plan_exists(file: File):
    """Test that checkbox test plan exists"""
    assert file.exists(
        "/usr/share/checkbox-provider-base/units/gardenlinux/test-plan.pxu"
    ), "Checkbox test plan should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-checkbox-config-checkbox-units-category",
    ]
)
@pytest.mark.feature("checkbox")
def test_checkbox_units_category_exists(file: File):
    """Test that checkbox category units exist"""
    assert file.exists(
        "/usr/share/checkbox-provider-base/units/gardenlinux/category.pxu"
    ), "Checkbox category units should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-checkbox-config-checkbox-units-jobs",
    ]
)
@pytest.mark.feature("checkbox")
def test_checkbox_units_jobs_exists(file: File):
    """Test that checkbox job units exist"""
    assert file.exists(
        "/usr/share/checkbox-provider-base/units/gardenlinux/jobs.pxu"
    ), "Checkbox job units should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-checkbox-config-checkbox-units-manifest",
    ]
)
@pytest.mark.feature("checkbox")
def test_checkbox_units_manifest_exists(file: File):
    """Test that checkbox manifest units exist"""
    assert file.exists(
        "/usr/share/checkbox-provider-base/units/gardenlinux/manifest.pxu"
    ), "Checkbox manifest units should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-checkbox-config-issue",
    ]
)
@pytest.mark.feature("checkbox")
def test_checkbox_issue_banner_exists(file: File):
    """Test that checkbox has issue banner file"""
    assert file.exists("/etc/issue"), "Checkbox issue banner should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-checkbox-config-issue",
    ]
)
@pytest.mark.feature("checkbox")
def test_checkbox_issue_banner_content(parse_file: ParseFile):
    """Test that checkbox has issue banner file"""
    expected_lines = ["Welcome to Garden Linux HW Testing Image"]
    assert expected_lines in parse_file.lines(
        "/etc/issue"
    ), "Checkbox issue banner should be correct"


@pytest.mark.setting_ids(
    [
        "GL-SET-checkbox-config-issue-net",
    ]
)
@pytest.mark.feature("checkbox")
def test_checkbox_issue_net_banner_exists(file: File):
    """Test that checkbox has network issue banner file"""
    assert file.exists("/etc/issue.net"), "Checkbox network issue banner should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-checkbox-config-issue-net",
    ]
)
@pytest.mark.feature("checkbox")
def test_checkbox_issue_net_banner_empty(file: File):
    """Test that checkbox has empty network issue banner file"""
    size = file.get_size("/etc/issue.net")
    assert size == 0, "Checkbox network issue.net banner should be empty"


@pytest.mark.setting_ids(
    [
        "GL-SET-checkbox-config-motd",
    ]
)
@pytest.mark.feature("checkbox")
def test_checkbox_motd_exists(file: File):
    """Test that checkbox has message of the day file"""
    assert file.exists("/etc/motd"), "Checkbox motd should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-checkbox-config-motd",
    ]
)
@pytest.mark.feature("checkbox")
def test_checkbox_motd_empty(file: File):
    """Test that checkbox has empty message of the day file"""
    size = file.get_size("/etc/motd")
    assert size == 0, "Checkbox motd should be empty"


@pytest.mark.setting_ids(
    [
        "GL-SET-checkbox-config-journald-10-logs",
    ]
)
@pytest.mark.feature("checkbox")
def test_checkbox_journald_logs_config_exists(file: File):
    """Test that checkbox has journald logs configuration"""
    assert file.exists(
        "/etc/systemd/journald.conf.d/10-logs.conf"
    ), "Checkbox journald logs configuration should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-checkbox-config-journald-10-logs",
    ]
)
@pytest.mark.feature("checkbox")
def test_checkbox_journald_logs_config_content(parse_file: ParseFile):
    """Test that checkbox has journald logs configuration"""
    config = parse_file.parse("/etc/systemd/journald.conf.d/10-logs.conf", format="ini")
    assert (
        config["Journal"]["ForwardToConsole"] == "no"
    ), "Checkbox journald logs configuration ForwardToConsole should be correct"
    assert (
        config["Journal"]["ForwardToWall"] == "no"
    ), "Checkbox journald logs configuration ForwardToWall should be correct"


@pytest.mark.setting_ids(
    [
        "GL-SET-checkbox-config-kernel-cmdline-iso",
    ]
)
@pytest.mark.feature("checkbox")
def test_checkbox_kernel_cmdline_iso_exists(file: File):
    """Test that checkbox has kernel cmdline ISO configuration"""
    assert file.exists(
        "/etc/kernel/cmdline.iso"
    ), "Checkbox kernel cmdline ISO configuration should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-checkbox-config-kernel-cmdline-iso",
    ]
)
@pytest.mark.feature("checkbox")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_checkbox_kernel_cmdline_iso_content(kernel_cmdline: List[str]):
    """Verify kernel cmdline ISO configuration parameters are present in the running kernel command line for checkbox."""
    assert (
        "console=tty0 rd.live.squashimg=squashfs.img root=live:CDLABEL=GardenlinuxISO rd.live.overlay.overlayfs rd.live.dir=live rd.live.ram quiet"
        in kernel_cmdline
    ), "Kernel cmdline ISO configuration should be correct"


@pytest.mark.setting_ids(
    [
        "GL-SET-checkbox-script-dmesg_colored",
    ]
)
@pytest.mark.feature("checkbox")
def test_checkbox_dmesg_colored_script_exists(file: File):
    """Test that checkbox has dmesg colored script"""
    assert file.exists(
        "/usr/lib/checkbox-provider-base/bin/dmesg_colored.sh"
    ), "Checkbox dmesg colored script should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-checkbox-script-generate-report",
    ]
)
@pytest.mark.feature("checkbox")
def test_checkbox_generate_report_script_exists(file: File):
    """Test that checkbox has generate report script"""
    assert file.exists(
        "/usr/local/bin/generate-report.sh"
    ), "Checkbox generate report script should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-checkbox-script-hw_encrypt_check",
    ]
)
@pytest.mark.feature("checkbox")
def test_checkbox_hw_encrypt_check_script_exists(file: File):
    """Test that checkbox has hardware encryption check script"""
    assert file.exists(
        "/usr/lib/checkbox-provider-base/bin/hw_encrypt_check.sh"
    ), "Checkbox hardware encryption check script should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-checkbox-script-tpm_check",
    ]
)
@pytest.mark.feature("checkbox")
def test_checkbox_tpm_check_script_exists(file: File):
    """Test that checkbox has TPM check script"""
    assert file.exists(
        "/usr/lib/checkbox-provider-base/bin/tpm_check.sh"
    ), "Checkbox TPM check script should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-checkbox-script-virtualization_disabled",
    ]
)
@pytest.mark.feature("checkbox")
def test_checkbox_virtualization_disabled_script_exists(file: File):
    """Test that checkbox has virtualization disabled check script"""
    assert file.exists(
        "/usr/lib/checkbox-provider-base/bin/virtualization_disabled.sh"
    ), "Checkbox virtualization disabled script should exist"
