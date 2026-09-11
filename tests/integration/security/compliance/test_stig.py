import pytest
from plugins.file import File
from plugins.kernel_module import KernelModule
from plugins.parse_file import ParseFile


@pytest.mark.testcov(["GL-TESTCOV-stig-config-modprobe-usb-disable"])
@pytest.mark.feature("stig")
def test_stig_usb_disabled(file: File):
    """Test that USB is disabled via modprobe"""
    assert file.is_regular_file("/etc/modprobe.d/disabled_usb.conf")


@pytest.mark.testcov(["GL-TESTCOV-stig-config-modprobe-usb-disable"])
@pytest.mark.feature("stig")
@pytest.mark.booted(reason="Modules can only be loaded on booted system")
def test_stig_modprobe_disable_modules_not_loaded(kernel_module: KernelModule):
    """Test that disabled modules are not loaded"""
    modules = [
        "usbcore",
        "usb-common",
        "usb-storage",
    ]
    for module in modules:
        assert not kernel_module.is_module_loaded(
            module
        ), f"Module {module} is loaded but should be deny listed"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-rsyslog-default"])
@pytest.mark.feature("disaSTIGmedium")
def test_stig_rsyslog_default_exists(file: File):
    """Test that STIG rsyslog default config exists"""
    assert file.is_regular_file("/etc/rsyslog.d/50-default.conf")


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-rsyslog-default"])
@pytest.mark.feature("disaSTIGmedium")
def test_stig_rsyslog_default_content(parse_file: ParseFile):
    """Test that STIG rsyslog default config content exists"""
    lines = parse_file.lines("/etc/rsyslog.d/50-default.conf")
    assert (
        "auth.*,authpriv.* /var/log/secure" in lines
    ), "rsyslog default config should contain the correct content"
    assert (
        "daemon.* /var/log/messages" in lines
    ), "rsyslog default config should contain the correct content"
