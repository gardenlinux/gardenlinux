import pytest
from plugins.file import File
from plugins.initrd import Initrd
from plugins.systemd import Systemd

# =============================================================================
# Main _ignite Feature
# =============================================================================


@pytest.mark.testcov(
    [
        "GL-TESTCOV-_ignite-config-initrd-ignition",
    ]
)
@pytest.mark.feature("_ignite and not _usi")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_ignite_initrd_ignition_modules(initrd: Initrd):
    """Test that ignition dracut modules are present in initrd"""
    modules = [
        "ignition",
        "ignition-extra",
        "systemd-networkd",
    ]

    missing = [
        module for module in modules if not initrd.contains_dracut_module(module)
    ]
    assert (
        not missing
    ), f"The following dracut modules were not found in initrd: {', '.join(missing)}"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-_ignite-config-initrd-module-ignition-after-net-online",
        "GL-TESTCOV-_ignite-config-initrd-module-ignition-env-generator",
        "GL-TESTCOV-_ignite-config-initrd-module-ignition-files",
        "GL-TESTCOV-_ignite-config-initrd-module-ignition-module-setup",
    ]
)
@pytest.mark.feature("_ignite and not _usi")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_ignite_initrd_files(initrd: Initrd):
    """Test that files are present in initrd

    TODO: _usi feature uses a custom dracut build that excludes ignition dracut modules
    and doesn't include ignition files via initrd.include directory. This needs to be
    fixed by creating features/_ignite/initrd.include/ with the required files or a similar approach.
    See: features/_usi/image.esp.tar for the custom dracut build process.
    """
    paths = [
        "etc/systemd/system/ignition-fetch.service.d/after-net-online.conf",
        "usr/lib/systemd/system-generators/ignition-env-generator",
        "etc/ignition-files.env",
    ]

    missing = [path for path in paths if not initrd.contains_file(path)]
    assert (
        not missing
    ), f"The following files were not found in initrd: {', '.join(missing)}"


# =============================================================================
# _usi Feature
# =============================================================================


@pytest.mark.testcov(
    [
        "GL-TESTCOV-_usi-config-no-initrd-ignition",
    ]
)
@pytest.mark.feature("_usi")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test__usi_initrd_ignition_modules(initrd: Initrd):
    """Test that no ignition dracut modules are present in initrd"""
    modules = [
        "ignition",
        "ignition-extra",
        "systemd-networkd",
    ]

    missing = [
        module for module in modules if not initrd.contains_dracut_module(module)
    ]
    assert (
        missing
    ), f"The following dracut modules should not be found in initrd, but these were missing: {', '.join(missing)}"


@pytest.mark.testcov(["GL-TESTCOV-_usi-config-no-kernel-cmdline-ignition"])
@pytest.mark.feature("_usi")
def test_usi_no_ignition_cmdline_config(file: File):
    """Test that ignition kernel cmdline config does not exist"""
    assert not file.exists("/etc/kernel/cmdline.d/50-ignition.cfg")


@pytest.mark.testcov(["GL-TESTCOV-_usi-service-no-ignition-disable"])
@pytest.mark.feature("_usi")
@pytest.mark.booted(reason="Requires systemd")
def test__usi_no_ignition_disable_service(systemd: Systemd):
    """Test that ignition-disable.service is not installed"""
    assert not any(
        u.unit == "ignition-disable.service" for u in systemd.list_installed_units()
    )


# =============================================================================
# kvm Feature
# =============================================================================

# Cannot not be tested as 50-ignition.cfg is deleted by ignition-disable.service.
# @pytest.mark.testcov(["GL-TESTCOV-kvm-config-kernel-cmdline-ignition"])
# @pytest.mark.feature("vmware")
# @pytest.mark.arch("amd64")
# def test_kvm_kernel_cmdline_ignition_exists(file: File):
#     """Test that KVM does have ignition kernel cmdline. It never exists on arm64."""
#     assert file.exists("/etc/kernel/cmdline.d/50-ignition.cfg")

# Cannot not be tested as 50-ignition.cfg is deleted by ignition-disable.service.
# @pytest.mark.testcov(["GL-TESTCOV-kvm-config-kernel-cmdline-ignition"])
# @pytest.mark.feature("kvm")
# @pytest.mark.booted(reason="kernel cmdline needs a booted system")
# def test_ignition_configuration_in_cmdline_kvm(kernel_cmdline: List[str]):
#     """Verify ignition parameters are present in the running kernel command line for KVM."""
#     settings = [
#         "ignition.firstboot=1",
#         "ignition.platform.id=qemu",
#     ]
#     missing = [setting for setting in settings if setting not in kernel_cmdline]
#     assert (
#         not missing
#     ), f"The following kernel cmdline parameters were not found: {', '.join(missing)}"


@pytest.mark.testcov(["GL-TESTCOV-kvm-service-ignition-disable-unit"])
@pytest.mark.feature(
    "kvm and not _usi",
    reason="Ignition is enabled on KVM but disabled on _usi again",
)
def test_kvm_ignition_disable_unit_exists(file):
    """Test that ignition-disable.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/ignition-disable.service")


@pytest.mark.testcov(["GL-TESTCOV-kvm-service-ignition-disable-enable"])
@pytest.mark.feature(
    "kvm and not _usi",
    reason="Ignition is enabled on KVM but disabled on _usi again",
)
@pytest.mark.booted(reason="Requires systemd")
def test_kvm_ignition_disable_service_enabled(systemd: Systemd):
    """Test that ignition-disable.service is enabled"""
    assert systemd.is_enabled("ignition-disable.service")


@pytest.mark.testcov(["GL-TESTCOV-kvm-service-ignition-disable-enable"])
@pytest.mark.feature(
    "kvm and not _usi",
    reason="Ignition is enabled on KVM but disabled on _usi again",
)
@pytest.mark.booted(reason="Requires systemd")
def test_kvm_ignition_disable_service_active(systemd: Systemd):
    """Test that ignition-disable.service is active"""
    assert systemd.is_active("ignition-disable.service")


# =============================================================================
# vmware Feature
# =============================================================================


# Cannot not be tested as 50-ignition.cfg is deleted by ignition-disable.service.
# @pytest.mark.testcov(["GL-TESTCOV-vmware-config-kernel-cmdline-ignition"])
# @pytest.mark.feature("vmware")
# @pytest.mark.arch("amd64")
# def test_vmware_kernel_cmdline_ignition_exists(file: File):
#     """Test that VMware does have ignition kernel cmdline. It never exists on arm64."""
#     assert file.exists("/etc/kernel/cmdline.d/50-ignition.cfg")


# Cannot not be tested as 50-ignition.cfg is deleted by ignition-disable.service.
# @pytest.mark.testcov(["GL-TESTCOV-vmware-config-kernel-cmdline-ignition"])
# @pytest.mark.feature("vmware")
# @pytest.mark.arch("amd64")
# @pytest.mark.booted(reason="kernel cmdline needs a booted system")
# def test_ignition_configuration_in_cmdline_vmware_amd64(kernel_cmdline: List[str]):
#     """Verify ignition parameters are present in the running kernel command line for VMware."""
#     assert (
#         "ignition.firstboot=1 ignition.platform.id=vmware" in kernel_cmdline
#     ), "Ignition (ignition.firstboot=1 ignition.platform.id=vmware) not found in kernel cmdline"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-vmware-config-kernel-cmdline-no-ignition-arm64",
    ]
)
@pytest.mark.feature("vmware")
@pytest.mark.arch("arm64")
def test_vmware_kernel_cmdline_no_ignition_arm64(file: File):
    """Test that VMware does not have ignition kernel cmdline for ARM64"""
    assert not file.exists(
        "/etc/kernel/cmdline.d/50-ignition.cfg"
    ), "ARM64 ignition config should not exist"


# Cannot not be tested as 50-ignition.cfg is deleted by ignition-disable.service.
# @pytest.mark.testcov(["GL-TESTCOV-vmware-config-kernel-cmdline-ignition"])
# @pytest.mark.feature("vmware")
# @pytest.mark.arch("arm64")
# @pytest.mark.booted(reason="kernel cmdline needs a booted system")
# def test_no_ignition_configuration_in_cmdline_vmware_arm64(kernel_cmdline: List[str]):
#     """Verify no ignition parameters are present in the running kernel command line for VMware."""
#     assert (
#         "ignition.firstboot=1 ignition.platform.id=vmware" not in kernel_cmdline
#     ), "Ignition (ignition.firstboot=1 ignition.platform.id=vmware) found in kernel cmdline"


@pytest.mark.testcov(["GL-TESTCOV-vmware-service-ignition-disable-unit"])
@pytest.mark.feature("vmware")
def test_vmware_ignition_disable_unit_exists(file):
    """Test that ignition-disable.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/ignition-disable.service")
