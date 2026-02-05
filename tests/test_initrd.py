from pathlib import Path

import pytest
from plugins.initrd import Initrd
from plugins.parse_file import ParseFile


@pytest.mark.setting_ids(["GL-SET-aws-config-initrd-xen-blkfront"])
@pytest.mark.feature("aws")
def test_aws_dracut_contains_xen_modules(parse_file: ParseFile):
    file = "/etc/dracut.conf.d/90-xen-blkfront-driver.conf"
    line = 'add_drivers+=" xen-blkfront "'
    lines = parse_file.lines(file)
    assert line in lines, f"Could not find line {line} in {file}."


@pytest.mark.setting_ids(["GL-SET-aws-config-initrd-xen-blkfront"])
@pytest.mark.feature("aws")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_aws_initrd_contains_xen_modules(initrd: Initrd):
    modules = ["xen-blkfront"]
    for module in modules:
        assert initrd.contains_module(module), f"{module} module not found in initrd"


@pytest.mark.setting_ids(["GL-SET-azure-config-initrd-nvme"])
@pytest.mark.feature("azure")
def test_azure_dracut_contains_nvme_modules(parse_file: ParseFile):
    file = "/etc/dracut.conf.d/67-azure-nvme-modules.conf"
    line = 'add_drivers+=" nvme nvme-core nvme-fabrics nvme-fc nvme-rdma nvme-loop nvmet nvmet-fc nvme-tcp "'
    lines = parse_file.lines(file)
    assert line in lines, f"Could not find line {line} in {file}."


@pytest.mark.setting_ids(["GL-SET-azure-config-initrd-nvme"])
@pytest.mark.feature("azure")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_azure_initrd_contains_nvme_modules(initrd: Initrd):
    modules = ["nvme-fabrics", "nvme-fc", "nvme-rdma"]
    for module in modules:
        assert initrd.contains_module(module), f"{module} module not found in initrd"


@pytest.mark.setting_ids(["GL-SET-openstackbaremetal-config-initrd-bnxt"])
@pytest.mark.feature("openstackbaremetal")
def test_openstackbaremetal_dracut_contains_broadcom_modules(parse_file: ParseFile):
    file = "/etc/dracut.conf.d/49-include-bnxt-drivers.conf"
    line = 'add_drivers+=" bnxt_en "'
    lines = parse_file.lines(file)
    assert line in lines, f"Could not find line {line} in {file}."


@pytest.mark.setting_ids(["GL-SET-openstackbaremetal-config-initrd-bnxt"])
@pytest.mark.feature("openstackbaremetal")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_openstackbaremetal_initrd_contains_broadcom_modules(initrd: Initrd):
    modules = ["bnxt_en"]
    for module in modules:
        assert initrd.contains_module(module), f"{module} module not found in initrd"


# -------------------------------------------------------------------
# ################### DRACUT MODULES ################################
# -------------------------------------------------------------------


@pytest.mark.setting_ids(
    [
        # bfpxe
        "GL-SET-bfpxe-config-initrd-module-gardenlinux-live-any",
        "GL-SET-bfpxe-config-initrd-module-gardenlinux-live-cleanup",
        "GL-SET-bfpxe-config-initrd-module-gardenlinux-live-get-squashfs",
        "GL-SET-bfpxe-config-initrd-module-gardenlinux-live-gl-end",
        "GL-SET-bfpxe-config-initrd-module-gardenlinux-live-is-live-image",
        "GL-SET-bfpxe-config-initrd-module-gardenlinux-live-module-setup",
        "GL-SET-bfpxe-config-initrd-module-gardenlinux-live-overlay-setup",
        "GL-SET-bfpxe-config-initrd-module-gardenlinux-live-squash-mount-generator",
        "GL-SET-bfpxe-config-initrd-module-gardenlinux-live-sysroot-generator",
        "GL-SET-bfpxe-config-initrd-gl-live",
        # pxe
        "GL-SET-_pxe-config-initrd-module-gardenlinux-live-any",
        "GL-SET-_pxe-config-initrd-module-gardenlinux-live-cleanup",
        "GL-SET-_pxe-config-initrd-module-gardenlinux-live-gl-end",
        "GL-SET-_pxe-config-initrd-module-gardenlinux-live-is-live-image",
        "GL-SET-_pxe-config-initrd-module-gardenlinux-live-live-get-squashfs",
        "GL-SET-_pxe-config-initrd-module-gardenlinux-live-live-overlay-setup",
        "GL-SET-_pxe-config-initrd-module-gardenlinux-live-live-sysroot-generator",
        "GL-SET-_pxe-config-initrd-module-gardenlinux-live-module-setup",
        "GL-SET-_pxe-config-initrd-module-gardenlinux-live-squash-mount-generator",
        "GL-SET-_pxe-config-initrd-gl-live",
        # ignition
        "GL-SET-_ignite-config-initrd-ignition",
        "GL-SET-_ignite-config-initrd-module-ignition-module-setup",
        "GL-SET-_ignite-config-initrd-module-ignition-files",
        "GL-SET-_ignite-config-initrd-module-ignition-after-net-online",
        "GL-SET-_ignite-config-initrd-module-ignition-env-generator",
    ]
)
@pytest.mark.root
@pytest.mark.booted
def test_initrd_required_modules_present(initrd: Initrd):
    modules = [
        "gardenlinux-live-any",
        "gardenlinux-live-cleanup",
        "gardenlinux-live-get-squashfs",
        "gardenlinux-live-gl-end",
        "gardenlinux-live-is-live-image",
        "gardenlinux-live-module-setup",
        "gardenlinux-live-overlay-setup",
        "gardenlinux-live-squash-mount-generator",
        "gardenlinux-live-sysroot-generator",
        "ignition",
        "ignition-env-generator",
    ]

    for module in modules:
        assert initrd.contains_module(module)


# -------------------------------------------------------------------
# ################### INITRD SCRIPTS ################################
# -------------------------------------------------------------------


@pytest.mark.setting_ids(
    [
        "GL-SET-_kdump-script-prepare-initrd-kdump",
        "GL-SET-_tpm2-script-initrd-check-tpm",
        "GL-SET-_tpm2-script-initrd-measure-pcr7",
        "GL-SET-_trustedboot-script-initrd-check-secureboot",
    ]
)
@pytest.mark.root
@pytest.mark.booted
def test_initrd_scripts_present(initrd: Initrd):
    scripts = [
        "usr/lib/dracut/modules.d/50kdump/prepare-kdump.sh",
        "usr/lib/dracut/modules.d/90tpm2/check-tpm.sh",
        "usr/lib/dracut/modules.d/90tpm2/measure-pcr7.sh",
        "usr/lib/dracut/modules.d/90trustedboot/check-secureboot.sh",
    ]

    for path in scripts:
        assert initrd.contains_file(path)


# -------------------------------------------------------------------
# ################### INITRD SYSTEMD UNITS ##########################
# -------------------------------------------------------------------


@pytest.mark.setting_ids(
    [
        "GL-SET-_tpm2-service-initrd-check-tpm",
        "GL-SET-_tpm2-service-initrd-switch-root-tpm2-measure",
        "GL-SET-_tpm2-service-initrd-systemd-cryptsetup-var",
        "GL-SET-_tpm2-service-initrd-systemd-repart-check-tpm",
        "GL-SET-_tpm2-service-initrd-tpm2-measure",
        "GL-SET-_trustedboot-service-initrd-emergency",
        "GL-SET-_ephemeral-service-initrd-ephemeral-cryptsetup",
        "GL-SET-_trustedboot-service-initrd-local-fs-target-requires-check-secureboot",
    ]
)
@pytest.mark.root
@pytest.mark.booted
def test_initrd_services_present(initrd: Initrd):
    units = [
        "usr/lib/systemd/system/tpm2-check.service",
        "usr/lib/systemd/system/tpm2-measure.service",
        "usr/lib/systemd/system/systemd-cryptsetup@var.service",
        "usr/lib/systemd/system/systemd-repart.service",
        "usr/lib/systemd/system/trustedboot-emergency.service",
        "usr/lib/systemd/system/ephemeral-cryptsetup.service",
        "usr/lib/systemd/system/local-fs.target.requires/check-secureboot.service",
    ]

    for unit in units:
        assert initrd.contains_file(unit)


# -------------------------------------------------------------------
# ################### MOUNT / REPART UNITS ##########################
# -------------------------------------------------------------------


@pytest.mark.setting_ids(
    [
        "GL-SET-_ephemeral-config-initrd-mount-var",
        "GL-SET-_ephemeral-config-initrd-repart-var",
        "GL-SET-_nocrypt-config-initrd-mount-var",
        "GL-SET-_nocrypt-config-initrd-repart-var",
        "GL-SET-_tpm2-config-initrd-mount-var",
        "GL-SET-_tpm2-config-initrd-repart-var",
    ]
)
@pytest.mark.root
@pytest.mark.booted
def test_initrd_mount_and_repart_configs_present(initrd: Initrd):
    paths = [
        "usr/lib/systemd/system/var.mount",
        "usr/lib/systemd/repart.d/var.conf",
    ]

    for path in paths:
        assert initrd.contains_file(path)


@pytest.mark.setting_ids(
    [
        "GL-SET-kvm-config-no-initrd-img",
        "GL-SET-kvm-config-no-initrd-img-old",
        "GL-SET-server-config-no-initrd-img",
        "GL-SET-server-config-no-initrd-img-old",
        "GL-SET-server-config-initrd-general",
        "GL-SET-server-config-initrd-uefi-stub",
    ]
)
def test_no_initrd_images_present():
    forbidden = [
        "/boot/initrd.img",
        "/boot/initrd.img.old",
    ]

    for path in forbidden:
        assert not Path(path).exists()


# -------------------------------------------------------------------
# ################### USI / GENERATORS / MISC #######################
# -------------------------------------------------------------------


@pytest.mark.setting_ids(
    [
        "GL-SET-_usi-config-initrd-mount-initrd-root-fs-target-requires-sysroot-etc-mount",
        "GL-SET-_usi-config-initrd-mount-initrd-root-fs-target-requires-sysroot-home-mount",
        "GL-SET-_usi-config-initrd-mount-initrd-root-fs-target-requires-sysroot-mount",
        "GL-SET-_usi-config-initrd-mount-initrd-root-fs-target-requires-sysroot-opt-mount",
        "GL-SET-_usi-config-initrd-mount-initrd-root-fs-target-requires-sysroot-root-mount",
        "GL-SET-_usi-config-initrd-mount-sysroot-etc-mount",
        "GL-SET-_usi-config-initrd-mount-sysroot-home-mount",
        "GL-SET-_usi-config-initrd-mount-sysroot-mount",
        "GL-SET-_usi-config-initrd-mount-sysroot-opt-mount",
        "GL-SET-_usi-config-initrd-mount-sysroot-root-mount",
        "GL-SET-_usi-config-initrd-repart-efi",
        "GL-SET-_usi-config-initrd-script-repart-esp-disk",
        "GL-SET-_usi-config-initrd-systemd-system-generators-detect-disk-by-efivars",
        "GL-SET-_pxe-config-initrd-omit-cdc-ether",
    ]
)
@pytest.mark.root
@pytest.mark.booted
def test_initrd_usi_and_misc_files_present(initrd: Initrd):
    paths = [
        "usr/lib/systemd/system/sysroot.mount",
        "usr/lib/systemd/system/sysroot-etc.mount",
        "usr/lib/systemd/system/sysroot-home.mount",
        "usr/lib/systemd/system/sysroot-opt.mount",
        "usr/lib/systemd/system/sysroot-root.mount",
        "usr/lib/systemd/repart.d/efi.conf",
        "usr/lib/systemd/system-generators/detect-disk-by-efivars",
        "usr/lib/dracut/modules.d/90usi/repart-esp-disk.sh",
        "usr/lib/dracut/modules.d/90pxe/omit-cdc-ether.sh",
    ]

    for path in paths:
        assert initrd.contains_file(path)


@pytest.mark.setting_ids(["GL-SET-config-initrd-no-ignition"])
@pytest.mark.root
@pytest.mark.booted
def test_initrd_no_ignition(initrd: Initrd):
    assert not initrd.contains_module("ignition")
