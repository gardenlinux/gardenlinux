import pytest
from plugins.initrd import Initrd
from plugins.systemd import Systemd

# =============================================================================
# Main _ignite Feature
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-_ignite-config-initrd-ignition",
    ]
)
@pytest.mark.feature("_ignite")
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


@pytest.mark.setting_ids(
    [
        "GL-SET-_ignite-config-initrd-module-ignition-after-net-online",
        "GL-SET-_ignite-config-initrd-module-ignition-env-generator",
        "GL-SET-_ignite-config-initrd-module-ignition-files",
        "GL-SET-_ignite-config-initrd-module-ignition-module-setup",
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


@pytest.mark.setting_ids(
    [
        "GL-SET-_usi-config-no-initrd-ignition",
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
    ), f"The following dracut modules were found in initrd: {', '.join(missing)}"


@pytest.mark.setting_ids(["GL-SET-_usi-service-no-ignition-disable"])
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


@pytest.mark.setting_ids(["GL-SET-kvm-service-ignition-disable-unit"])
@pytest.mark.feature(
    "kvm and not _usi",
    reason="Ignition is disabled on KVM but re-enabled on _usi again",
)
def test_kvm_ignition_disable_unit_exists(file):
    """Test that ignition-disable.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/ignition-disable.service")


@pytest.mark.setting_ids(["GL-SET-kvm-service-ignition-disable-enable"])
@pytest.mark.feature(
    "kvm and not _usi",
    reason="Ignition is disabled on KVM but re-enabled on _usi again",
)
@pytest.mark.booted(reason="Requires systemd")
def test_kvm_ignition_disable_service_enabled(systemd: Systemd):
    """Test that ignition-disable.service is enabled"""
    assert systemd.is_enabled("ignition-disable.service")


@pytest.mark.setting_ids(["GL-SET-kvm-service-ignition-disable-enable"])
@pytest.mark.feature(
    "kvm and not _usi",
    reason="Ignition is disabled on KVM but re-enabled on _usi again",
)
@pytest.mark.booted(reason="Requires systemd")
def test_kvm_ignition_disable_service_active(systemd: Systemd):
    """Test that ignition-disable.service is active"""
    assert systemd.is_active("ignition-disable.service")


# =============================================================================
# vmware Feature
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-vmware-service-ignition-disable-unit"])
@pytest.mark.feature("vmware")
def test_vmware_ignition_disable_unit_exists(file):
    """Test that ignition-disable.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/ignition-disable.service")
