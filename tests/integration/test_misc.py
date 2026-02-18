import pytest
from plugins.file import File
from plugins.parse_file import ParseFile
from plugins.shell import ShellRunner
from plugins.sysctl import Sysctl
from plugins.systemd import Systemd

# =============================================================================
# _usi Feature
# =============================================================================


@pytest.mark.setting_ids(
    [
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
        "/etc/update-motd.d/25-secureboot",
        "/usr/local/sbin/update-kernel-cmdline",
        "/usr/sbin/enroll-gardenlinux-secureboot-keys",
    ]

    missing = [path for path in paths if not file.exists(path)]
    assert not missing, f"The following files were not found: {', '.join(missing)}"


@pytest.mark.setting_ids(["GL-SET-_usi-config-no-root-home"])
@pytest.mark.feature("_usi")
def test_usi_empty_root_home_directory(file: File):
    """Test that root home directory does not exist"""
    assert not file.exists("/root/*"), "The root home directory should be empty"
    assert not file.exists(
        "/root/.*"
    ), "The root home directory should not contain any hidden files"


@pytest.mark.setting_ids(["GL-SET-_usi-config-no-udev-rules-image-dissect"])
@pytest.mark.feature("_usi")
def test_usi_no_udev_rules_image_dissect(file: File):
    """Test that udev rules for image dissect do not exist"""
    assert not file.exists("/usr/lib/udev/rules.d/90-image-dissect.rules")


# =============================================================================
# cisPartition Feature
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-cisPartition-config-mount-tmp"])
@pytest.mark.feature("cisPartition")
def test_cispartition_mount_files_exists(file: File):
    """Test that mount files exist"""
    paths = [
        "/etc/systemd/system/tmp.mount",
    ]

    missing = [path for path in paths if not file.exists(path)]
    assert not missing, f"The following files were not found: {', '.join(missing)}"


@pytest.mark.setting_ids(["GL-SET-cisPartition-config-mount-tmp-enable"])
@pytest.mark.feature("cisPartition")
@pytest.mark.booted(reason="Requires systemd")
def test_cispartition_mount_units_enabled(systemd: Systemd):
    """Test that mount units are enabled"""
    paths = [
        "tmp.mount",
    ]

    missing = [path for path in paths if not systemd.is_enabled(path)]
    assert not missing, f"The following units were not enabled: {', '.join(missing)}"


# =============================================================================
# cisSysctl Feature
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-cisSysctl-config-sysctl-cis"])
@pytest.mark.feature("cisSysctl")
def test_cissysctl_sysctl_files_exists(file: File):
    """Test that CIS sysctl configuration file exists"""
    paths = [
        "/etc/sysctl.d/99-cis.conf",
    ]

    missing = [path for path in paths if not file.exists(path)]
    assert not missing, f"The following files were not found: {', '.join(missing)}"


@pytest.mark.setting_ids(["GL-SET-cisSysctl-config-sysctl-cis"])
@pytest.mark.feature("cisSysctl")
@pytest.mark.booted(reason="sysctl needs a booted system")
def test_cissysctl_sysctl_parameters_set(sysctl: Sysctl):
    """Test that CIS sysctl parameters are set"""
    parameters = [
        "net.ipv4.conf.all.forwarding=0",
        "net.ipv4.conf.all.accept_redirects=0",
        "net.ipv4.conf.default.accept_redirects=0",
        "net.ipv6.conf.all.accept_redirects=0",
        "net.ipv6.conf.default.accept_redirects=0",
        "net.ipv4.conf.all.secure_redirects=0",
        "net.ipv4.conf.default.secure_redirects=0",
        "net.ipv4.conf.all.log_martians=1",
        "net.ipv4.conf.default.log_martians=1",
        "net.ipv4.conf.all.rp_filter=1",
        "net.ipv4.conf.default.rp_filter=1",
        "net.ipv6.conf.all.disable_ipv6=1",
        "net.ipv6.conf.default.disable_ipv6=1",
        "net.ipv6.conf.lo.disable_ipv6=0",
        "net.ipv4.conf.all.send_redirects=0",
        "net.ipv4.conf.default.send_redirects=0",
        "net.ipv4.conf.default.accept_source_route=0",
        "fs.suid_dumpable=0",
    ]
    missing = [
        parameter.split("=")[0]
        for parameter in parameters
        if parameter.split("=")[0] not in sysctl
    ]
    assert (
        not missing
    ), f"The following parameters were not set to the expected value: {', '.join(missing)}"


# =============================================================================
# glvd Feature
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-glvd-script-update-motd-glvd"])
@pytest.mark.feature("glvd")
def test_glvd_motd_scripts_exists(file: File):
    """Test that GLVD MOTD script exists"""
    paths = [
        "/etc/update-motd.d/99-glvd",
    ]

    missing = [path for path in paths if not file.exists(path)]
    assert not missing, f"The following files were not found: {', '.join(missing)}"


# =============================================================================
# sapmachine Feature
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-sapmachine-config-apt-keyrings-sapmachine"])
@pytest.mark.feature("sapmachine")
def test_sapmachine_apt_keyring_exists(file):
    """Test that SapMachine APT keyring exists"""
    assert file.is_regular_file("/etc/apt/keyrings/sapmachine-apt-keyring.gpg")


# =============================================================================
# _unsigned Feature
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-_unsigned-config-efi-binary-exists"])
@pytest.mark.feature("_unsigned")
@pytest.mark.arch("amd64")
def test_unsigned_efi_binary_exists_amd64(file):
    """Test that unsigned EFI binary exists for amd64"""
    assert file.is_regular_file("/efi/EFI/BOOT/BOOTX64.EFI")


@pytest.mark.setting_ids(["GL-SET-_unsigned-config-efi-binary-exists"])
@pytest.mark.feature("_unsigned")
@pytest.mark.arch("arm64")
def test_unsigned_efi_binary_exists_arm64(file):
    """Test that unsigned EFI binary exists for arm64"""
    assert file.is_regular_file("/efi/EFI/BOOT/BOOTAA64.EFI")


# =============================================================================
# _fwcfg Feature
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-_fwcfg-script-run-qemu-fw_cfg-script"])
@pytest.mark.feature("_fwcfg")
def test_fwcfg_run_script_exists(file: File):
    """Test that qemu-fw_cfg run script exists"""
    assert file.is_regular_file("/usr/bin/run-qemu-fw_cfg-script")


# =============================================================================
# _slim Feature
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-_slim-config-no-docs-001"])
@pytest.mark.feature("_slim")
def test_slim_no_usr_share_docs_no_subdirs_exist(file: File):
    """Test that /usr/share/doc has no subdirectories"""
    from pathlib import Path

    doc_path = Path("/usr/share/doc")
    subdirs = [str(p.name) for p in doc_path.iterdir()] if doc_path.exists() else []
    assert not file.exists(
        "/usr/share/doc/*"
    ), f"The following subdirectories were found: {', '.join(subdirs)}"


@pytest.mark.setting_ids(["GL-SET-_slim-config-no-docs-002"])
@pytest.mark.feature("_slim")
def test_slim_no_usr_share_man_exists(file: File):
    """Test that /usr/share/man and other directories do not exist"""
    paths = [
        "/usr/share/man",
        "/usr/share/locale",
        "/usr/share/groff",
        "/usr/share/lintian",
        "/usr/share/linda",
    ]
    missing = [path for path in paths if file.exists(path)]
    assert (
        not missing
    ), f"The following directories do exist: {', '.join(missing)} but should not"


# =============================================================================
# ali Feature - Resolved Configuration
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-ali-config-resolved"])
@pytest.mark.feature("ali")
def test_ali_resolved_config_exists(file: File):
    """Test that Alibaba Cloud systemd-resolved configuration exists"""
    assert file.is_regular_file("/etc/systemd/resolved.conf.d/00-gardenlinux-ali.conf")


# =============================================================================
# aws Feature - Resolved Configuration
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-aws-config-resolved"])
@pytest.mark.feature("aws")
def test_aws_resolved_config_exists(file: File):
    """Test that AWS systemd-resolved configuration exists"""
    assert file.is_regular_file("/etc/systemd/resolved.conf.d/00-gardenlinux-aws.conf")


# =============================================================================
# clamav Feature - Cron Configuration
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-clamav-config-cron-root",
    ]
)
@pytest.mark.feature("clamav")
def test_clamav_cron_exists(file: File):
    """Test that clamav cron job exists"""
    cron_locations = [
        "/var/spool/cron/crontabs/root",
    ]
    exists = any(file.exists(loc) for loc in cron_locations)
    assert (
        exists
    ), f"Clamav cron job should exist in one of: {', '.join(cron_locations)}"


@pytest.mark.setting_ids(
    [
        "GL-SET-clamav-config-cron-root",
    ]
)
@pytest.mark.feature("clamav")
def test_clamav_cron_content(parse_file: ParseFile):
    """Test that clamav cron job contains the correct content"""
    lines = parse_file.lines("/var/spool/cron/crontabs/root")
    assert lines == [
        "0 30 * * * root /usr/bin/clamscan -ri / >> /var/log/clamav/clamd.log",
    ], "Clamav cron job should contain the correct content"


# =============================================================================
# Boot & Security Features
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-_pxe-config-repart-no-root",
    ]
)
@pytest.mark.feature("_pxe")
def test_pxe_no_repart_root(file: File):
    """Test that PXE does not have repart root configuration"""
    assert not file.exists(
        "/etc/repart.d/root.conf"
    ), "PXE should not have repart root configuration"


@pytest.mark.setting_ids(
    [
        "GL-SET-_prod-config-security-limits-disable-core-dumps",
    ]
)
@pytest.mark.feature("_prod")
def test_prod_security_limits_no_core_dumps(file: File):
    """Test that production has security limits disabling core dumps"""
    assert file.exists(
        "/etc/security/limits.conf"
    ), "Production should have core dump limits"


@pytest.mark.setting_ids(
    [
        "GL-SET-_prod-config-security-limits-disable-core-dumps",
    ]
)
@pytest.mark.booted(reason="ulimit needs a booted system")
@pytest.mark.feature("_prod")
def test_prod_security_limits_no_core_dumps_check(shell: ShellRunner):
    """Test that production has security limits disabling core dumps"""
    result = shell("ulimit -Sc", capture_output=True)
    assert (
        result.stdout.strip() == "0"
    ), "Production should have core dump limits set to 0"


@pytest.mark.setting_ids(
    [
        "GL-SET-_prod-config-sysctl-coredump-disable",
    ]
)
@pytest.mark.feature("_prod")
def test_prod_sysctl_coredump_disable(file: File):
    """Test that production has sysctl disabling core dumps"""
    assert file.exists(
        "/etc/sysctl.d/99-disable-core-dump.conf"
    ), "Production should have sysctl coredump disable"


@pytest.mark.setting_ids(
    [
        "GL-SET-_prod-config-sysctl-coredump-disable",
    ]
)
@pytest.mark.feature("_prod")
@pytest.mark.booted(reason="sysctl needs a booted system")
def test_prod_sysctl_coredump_disable_check(sysctl: Sysctl):
    """Test that production has sysctl disabling core dumps"""
    assert (
        sysctl["fs.suid_dumpable"] == 0
    ), "Production should have sysctl coredump disable"
    assert (
        sysctl["kernel.core_pattern"] == "|/bin/false"
    ), "Production should have sysctl coredump pattern set to /bin/false"


@pytest.mark.setting_ids(
    [
        "GL-SET-_prod-config-systemd-coredump-disable",
    ]
)
@pytest.mark.feature("_prod")
def test_prod_systemd_coredump_disable(file: File):
    """Test that production has systemd coredump configuration"""
    assert file.exists(
        "/etc/systemd/coredump.conf.d/disable_coredump.conf"
    ), "Production should have systemd coredump disable config"


@pytest.mark.setting_ids(
    [
        "GL-SET-service-systemd-coredump-no-override",
    ]
)
@pytest.mark.feature("_prod")
def test_prod_no_systemd_coredump_service_override(file: File):
    """Test that production does not have systemd-coredump service override"""
    assert not file.exists(
        "/etc/systemd/system/systemd-coredump.service.d/override.conf"
    ), "Production should not have systemd-coredump service override"


@pytest.mark.setting_ids(
    [
        "GL-SET-_unsigned-config-efi-binary-exists",
        "GL-SET-_trustedboot-config-efi-binary-exists",
    ]
)
@pytest.mark.feature("_unsigned or _trustedboot")
@pytest.mark.booted(reason="Chroot environments have no populted '/efi' directory")
@pytest.mark.arch("amd64")
def test_amd64_efi_binary_exists(file: File):
    """Test that unsigned has EFI binary"""
    efi_path = "/efi/EFI/BOOT/BOOTX64.EFI"
    exists = file.exists(efi_path)
    assert exists, f"EFI boot binary should exist: {efi_path}"


@pytest.mark.setting_ids(
    [
        "GL-SET-_unsigned-config-efi-binary-exists",
        "GL-SET-_trustedboot-config-efi-binary-exists",
    ]
)
@pytest.mark.feature("_unsigned or _trustedboot")
@pytest.mark.booted(reason="Chroot environments have no populted '/efi' directory")
@pytest.mark.arch("arm64")
def test_arm64_efi_binary_exists(file: File):
    """Test that unsigned has EFI binary"""
    efi_path = "/efi/EFI/BOOT/BOOTAA64.EFI"
    exists = file.exists(efi_path)
    assert exists, f"EFI boot binary should exist: {efi_path}"


# =============================================================================
# Cloud Platform Completions
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-lima-config-kernel-postinst-cmdline",
    ]
)
@pytest.mark.feature("lima")
def test_lima_kernel_postinst_cmdline_exists(file: File):
    """Test that Lima has kernel postinst cmdline script"""
    assert file.exists(
        "/etc/kernel/postinst.d/00-kernel-cmdline"
    ), "Lima kernel postinst cmdline script should exist"


# =============================================================================
# Storage & Network
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-multipath-config-multipath-conf",
    ]
)
@pytest.mark.feature("multipath")
def test_multipath_config_exists(file: File):
    """Test that multipath configuration exists"""
    assert file.is_regular_file(
        "/etc/multipath.conf"
    ), "Multipath configuration should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-firewall-config-nftables-include",
    ]
)
@pytest.mark.feature("firewall")
def test_firewall_nft_default_config_exists(file: File):
    """Test that firewall nft default configuration exists"""
    assert file.exists(
        "/etc/nft.d/default.conf"
    ), "Firewall nft default configuration should exist"


# =============================================================================
# Virtualization - KVM
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-kvm-config-udev-rules-onmetal",
    ]
)
@pytest.mark.feature("kvm")
def test_kvm_udev_rules_onmetal_exists(file: File):
    """Test that KVM udev rules for OnMetal exist"""
    assert file.exists(
        "/etc/udev/rules.d/60-onmetal.rules"
    ), "KVM OnMetal udev rules should exist"
