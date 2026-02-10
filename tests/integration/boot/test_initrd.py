"""
Test initrd contents, dracut modules, and configurations across all Garden Linux features.
"""

from pathlib import Path
from typing import List

import pytest
from plugins.file import File
from plugins.initrd import Initrd
from plugins.parse_file import ParseFile

# =============================================================================
# _ephemeral Feature Initrd
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-_ephemeral-config-initrd-repart-var",
        "GL-SET-_ephemeral-service-initrd-ephemeral-cryptsetup-unit",
        "GL-SET-_ephemeral-config-initrd-mount-var",
    ]
)
@pytest.mark.feature("_ephemeral")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_ephemeral_initrd_files(initrd: Initrd):
    """Test that files are present in initrd"""
    paths = [
        "etc/repart.d/10-var.conf",
        "etc/systemd/system/ephemeral-cryptsetup.service",
        "etc/systemd/system/sysroot-var.mount",
    ]

    missing = [path for path in paths if not initrd.contains_file(path)]
    assert (
        not missing
    ), f"The following files were not found in initrd: {', '.join(missing)}"


# =============================================================================
# _kdump Feature Initrd
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-_kdump-config-kernel-cmdline-crashkernel",
        "GL-SET-_kdump-config-service-kdump-tools-override",
        "GL-SET-_kdump-script-prepare-initrd-kdump",
    ]
)
@pytest.mark.feature("_kdump")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_kdump_initrd_files(initrd: Initrd):
    """Test that files are present in initrd"""
    paths = [
        "etc/kernel/cmdline.d/90-crashkernel.cfg",
        "etc/systemd/system/kdump-tools.service.d/override.conf",
        "usr/local/sbin/prepare-initrd-kdump",
    ]

    missing = [path for path in paths if not initrd.contains_file(path)]
    assert (
        not missing
    ), f"The following files were not found in initrd: {', '.join(missing)}"


# =============================================================================
# _nocrypt Feature Initrd
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-_nocrypt-config-initrd-repart-var",
        "GL-SET-_nocrypt-config-initrd-mount-var",
    ]
)
@pytest.mark.feature("_nocrypt")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_nocrypt_initrd_files(initrd: Initrd):
    """Test that files are present in initrd"""
    paths = ["etc/repart.d/10-var.conf", "etc/systemd/system/sysroot-var.mount"]

    missing = [path for path in paths if not initrd.contains_file(path)]
    assert (
        not missing
    ), f"The following files were not found in initrd: {', '.join(missing)}"


# =============================================================================
# _pxe Feature Initrd
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-_pxe-config-initrd-gl-live",
    ]
)
@pytest.mark.feature("_pxe")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_pxe_initrd_gl_live_module(initrd: Initrd):
    """Test that gl-live dracut module is present in initrd"""
    modules = ["gardenlinux-live"]

    for module in modules:
        assert initrd.contains_dracut_module(
            module
        ), f"{module} dracut module not found in initrd"


@pytest.mark.setting_ids(
    [
        "GL-SET-_pxe-config-initrd-omit-cdc-ether",
    ]
)
@pytest.mark.feature("_pxe")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_pxe_initrd_omit_cdc_ether_module(initrd: Initrd):
    """Test that omit-cdc-ether module is not present in initrd"""
    assert not initrd.contains_module(
        "cdc_ether"
    ), "cdc_ether module should not be in initrd"


@pytest.mark.setting_ids(
    [
        "GL-SET-_pxe-config-initrd-gl-live",
        "GL-SET-_pxe-config-initrd-omit-cdc-ether",
        "GL-SET-_pxe-config-kernel-cmdline-pxe",
        "GL-SET-_pxe-config-initrd-module-gardenlinux-live-any",
        "GL-SET-_pxe-config-initrd-module-gardenlinux-live-cleanup",
        "GL-SET-_pxe-config-initrd-module-gardenlinux-live-gl-end-unit",
        "GL-SET-_pxe-config-initrd-module-gardenlinux-live-is-live-image",
        "GL-SET-_pxe-config-initrd-module-gardenlinux-live-live-get-squashfs",
        "GL-SET-_pxe-config-initrd-module-gardenlinux-live-live-overlay-setup",
        "GL-SET-_pxe-config-initrd-module-gardenlinux-live-live-sysroot-generator",
        "GL-SET-_pxe-config-initrd-module-gardenlinux-live-module-setup",
        "GL-SET-_pxe-config-initrd-module-gardenlinux-live-squash-mount-generator",
    ]
)
@pytest.mark.feature("_pxe")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_pxe_initrd_files(initrd: Initrd):
    """Test that files are present in initrd"""
    paths = [
        "etc/systemd/system/systemd-networkd-wait-online.service.d/99-zany.conf",
        "var/lib/dracut/hooks/cleanup/00-cleanup.sh",
        "usr/lib/systemd/system/gl-end.service",
        "etc/systemd/system/initrd-switch-root.target.wants/gl-end.service",
        "usr/bin/is-live-image",
        "sbin/live-get-squashfs",
        "usr/lib/systemd/system-generators/live-overlay-setup",
        "usr/lib/systemd/system-generators/live-sysroot-generator",
        "usr/lib/systemd/system-generators/squash-mount-generator",
    ]

    missing = [path for path in paths if not initrd.contains_file(path)]
    assert (
        not missing
    ), f"The following files were not found in initrd: {', '.join(missing)}"


@pytest.mark.setting_ids(
    [
        "GL-SET-_pxe-config-kernel-cmdline-pxe",
    ]
)
@pytest.mark.feature("_pxe")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_pxe_kernel_cmdline(kernel_cmdline: List[str]):
    """Verify kernel command line parameters are present in the running kernel command line for PXE"""
    required_params = ["ip=dhcp", "gl.live=1", "gl.ovl=/:tmpfs"]
    missing = [param for param in required_params if param not in kernel_cmdline]
    assert (
        not missing
    ), f"The following kernel cmdline parameters were not found: {', '.join(missing)}"


# =============================================================================
# _tpm2 Feature Initrd
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-_tpm2-config-initrd-repart-var",
        "GL-SET-_tpm2-service-initrd-check-tpm-unit",
        "GL-SET-_tpm2-service-initrd-switch-root-tpm2-measure-unit",
        "GL-SET-_tpm2-config-initrd-mount-var",
        "GL-SET-_tpm2-service-initrd-systemd-cryptsetup-var-unit",
        "GL-SET-_tpm2-service-initrd-systemd-repart-check-tpm-unit",
        "GL-SET-_tpm2-service-initrd-tpm2-measure-unit",
        "GL-SET-_tpm2-script-initrd-check-tpm"
        "GL-SET-_tpm2-script-initrd-measure-pcr7",
    ]
)
@pytest.mark.feature("_tpm2")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_tpm2_initrd_files(initrd: Initrd):
    """Test that files are present in initrd"""
    paths = [
        "etc/repart.d/10-var.conf",
        "etc/systemd/system/check-tpm.service",
        "etc/systemd/system/initrd-switch-root.target.requires/tpm2-measure.service",
        "etc/systemd/system/sysroot-var.mount",
        "etc/systemd/system/systemd-cryptsetup-var.service",
        "etc/systemd/system/systemd-repart.service.requires/check-tpm.service",
        "etc/systemd/system/tpm2-measure.service",
        "usr/bin/check-tpm",
        "usr/bin/measure-pcr7",
    ]

    missing = [path for path in paths if not initrd.contains_file(path)]
    assert (
        not missing
    ), f"The following files were not found in initrd: {', '.join(missing)}"


# =============================================================================
# _trustedboot Feature Initrd
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-_trustedboot-service-initrd-local-fs-target-requires-check-secureboot-unit",
        "GL-SET-_trustedboot-service-initrd-emergency-unit",
        "GL-SET-_trustedboot-script-initrd-check-secureboot",
    ]
)
@pytest.mark.feature("_trustedboot")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_trustedboot_initrd_files(initrd: Initrd):
    """Test that files are present in initrd"""
    paths = [
        "etc/systemd/system/local-fs.target.requires/check-secureboot.service",
        "etc/systemd/system/emergency.service",
        "usr/bin/check-secureboot",
    ]

    missing = [path for path in paths if not initrd.contains_file(path)]
    assert (
        not missing
    ), f"The following files were not found in initrd: {', '.join(missing)}"


@pytest.mark.setting_ids(
    [
        "GL-SET-_trustedboot-config-kernel-cmdline-no-rd-shell",
    ]
)
@pytest.mark.feature("_trustedboot")
@pytest.mark.booted(reason="kernel cmdline needs a booted system")
def test_trustedboot_kernel_cmdline(kernel_cmdline: List[str]):
    """Verify kernel command line parameters are present in the running kernel command line for Trusted Boot"""
    required_params = ["rd.shell=0", "rd.emergency=poweroff", "systemd.gpt_auto=0"]
    missing = [param for param in required_params if param not in kernel_cmdline]
    assert (
        not missing
    ), f"The following kernel cmdline parameters were not found: {', '.join(missing)}"


# =============================================================================
# _usi Feature Initrd
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-_usi-config-initrd-repart-efi",
        "GL-SET-_usi-config-initrd-mount-initrd-root-fs-target-requires-sysroot-etc-mount",
        "GL-SET-_usi-config-initrd-mount-initrd-root-fs-target-requires-sysroot-home-mount",
        "GL-SET-_usi-config-initrd-mount-initrd-root-fs-target-requires-sysroot-opt-mount",
        "GL-SET-_usi-config-initrd-mount-initrd-root-fs-target-requires-sysroot-root-mount",
        "GL-SET-_usi-config-initrd-mount-initrd-root-fs-target-requires-sysroot-mount",
        "GL-SET-_usi-config-initrd-mount-sysroot-etc-mount",
        "GL-SET-_usi-config-initrd-mount-sysroot-home-mount",
        "GL-SET-_usi-config-initrd-mount-sysroot-opt-mount",
        "GL-SET-_usi-config-initrd-mount-sysroot-root-mount",
        "GL-SET-_usi-config-initrd-mount-sysroot-mount",
        "GL-SET-_usi-config-initrd-systemd-system-generators-detect-disk-by-efivars",
        "GL-SET-_usi-config-initrd-script-repart-esp-disk",
    ]
)
@pytest.mark.feature("_usi")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test__usi_initrd_files(initrd: Initrd):
    """Test that files are present in initrd"""
    paths = [
        "etc/repart.d/00-efi.conf",
        "etc/systemd/system/initrd-root-fs.target.requires/sysroot-etc.mount",
        "etc/systemd/system/initrd-root-fs.target.requires/sysroot-home.mount",
        "etc/systemd/system/initrd-root-fs.target.requires/sysroot-opt.mount",
        "etc/systemd/system/initrd-root-fs.target.requires/sysroot-root.mount",
        "etc/systemd/system/initrd-root-fs.target.requires/sysroot.mount",
        "etc/systemd/system/sysroot-etc.mount",
        "etc/systemd/system/sysroot-home.mount",
        "etc/systemd/system/sysroot-opt.mount",
        "etc/systemd/system/sysroot-root.mount",
        "etc/systemd/system/sysroot.mount",
        "etc/systemd/system-generators/detect-disk-by-efivars",
        "usr/bin/repart-esp-disk",
    ]

    missing = [path for path in paths if not initrd.contains_file(path)]
    assert (
        not missing
    ), f"The following files were not found in initrd: {', '.join(missing)}"


# =============================================================================
# aws Feature Initrd
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-aws-config-initrd-xen-blkfront"])
@pytest.mark.feature("aws")
def test_aws_dracut_xen_modules_config(parse_file: ParseFile):
    """Test that dracut config includes xen-blkfront driver"""
    file = "/etc/dracut.conf.d/90-xen-blkfront-driver.conf"
    line = 'add_drivers+=" xen-blkfront "'
    lines = parse_file.lines(file)
    assert line in lines, f"Could not find line {line} in {file}."


@pytest.mark.setting_ids(["GL-SET-aws-config-initrd-xen-blkfront"])
@pytest.mark.feature("aws")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_aws_initrd_xen_modules(initrd: Initrd):
    """Test that xen-blkfront module is present in initrd"""
    modules = ["xen-blkfront"]
    for module in modules:
        assert initrd.contains_module(module), f"{module} module not found in initrd"


# =============================================================================
# azure Feature Initrd
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-azure-config-initrd-nvme"])
@pytest.mark.feature("azure")
def test_azure_dracut_nvme_modules_config(parse_file: ParseFile):
    """Test that dracut config includes nvme drivers"""
    file = "/etc/dracut.conf.d/67-azure-nvme-modules.conf"
    line = 'add_drivers+=" nvme nvme-core nvme-fabrics nvme-fc nvme-rdma nvme-loop nvmet nvmet-fc nvme-tcp "'
    lines = parse_file.lines(file)
    assert line in lines, f"Could not find line {line} in {file}."


@pytest.mark.setting_ids(["GL-SET-azure-config-initrd-nvme"])
@pytest.mark.feature("azure")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_azure_initrd_nvme_modules(initrd: Initrd):
    """Test that nvme modules are present in initrd"""
    modules = ["nvme-fabrics", "nvme-fc", "nvme-rdma"]
    for module in modules:
        assert initrd.contains_module(module), f"{module} module not found in initrd"


# =============================================================================
# kvm Feature Initrd
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-kvm-config-no-initrd-img",
        "GL-SET-kvm-config-no-initrd-img-old",
    ]
)
@pytest.mark.feature("kvm")
def test_kvm_no_initrd_images():
    """Test that initrd.img symlinks are not present for kvm"""
    forbidden = [
        "/boot/initrd.img",
        "/boot/initrd.img.old",
    ]

    missing = [path for path in forbidden if Path(path).exists()]
    assert not missing, f"The following paths should not exist: {', '.join(missing)}"


# =============================================================================
# openstackbaremetal Feature Initrd
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-openstackbaremetal-config-initrd-bnxt"])
@pytest.mark.feature("openstackbaremetal")
def test_openstackbaremetal_dracut_broadcom_modules_config(parse_file: ParseFile):
    """Test that dracut config includes Broadcom bnxt_en driver"""
    file = "/etc/dracut.conf.d/49-include-bnxt-drivers.conf"
    line = 'add_drivers+=" bnxt_en "'
    lines = parse_file.lines(file)
    assert line in lines, f"Could not find line {line} in {file}."


@pytest.mark.setting_ids(["GL-SET-openstackbaremetal-config-initrd-bnxt"])
@pytest.mark.feature("openstackbaremetal")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_openstackbaremetal_initrd_broadcom_modules(initrd: Initrd):
    """Test that bnxt_en module is present in initrd"""
    modules = ["bnxt_en"]
    missing = [module for module in modules if not initrd.contains_module(module)]
    assert (
        not missing
    ), f"The following modules were not found in initrd: {', '.join(missing)}"


@pytest.mark.setting_ids(
    [
        "GL-SET-openstackbaremetal-config-repart-root",
    ]
)
@pytest.mark.feature("openstackbaremetal")
def test_openstackbaremetal_repart_root_config(file: File):
    """Test that OpenStack bare metal has repart root configuration"""
    assert file.exists(
        "/etc/repart.d/root.conf"
    ), "OpenStack bare metal repart root configuration should exist"


# =============================================================================
# server Feature Initrd
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-no-initrd-img",
        "GL-SET-server-config-no-initrd-img-old",
        "GL-SET-server-config-initrd-general",
        "GL-SET-server-config-initrd-uefi-stub",
    ]
)
@pytest.mark.feature("server")
def test_server_no_initrd_images():
    """Test that initrd.img symlinks are not present for server"""
    forbidden = [
        "/boot/initrd.img",
        "/boot/initrd.img.old",
    ]

    missing = [path for path in forbidden if Path(path).exists()]
    assert not missing, f"The following paths should not exist: {', '.join(missing)}"
