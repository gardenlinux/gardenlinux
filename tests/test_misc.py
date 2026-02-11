import pytest
from plugins.file import File
from plugins.kernel_module import KernelModule
from plugins.parse_file import ParseFile
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
    assert not file.exists("/usr/lib/udev/rules.d/60-persistent-storage-tape.rules")


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
    assert file.is_regular_file("/boot/efi/EFI/BOOT/BOOTX64.EFI")


@pytest.mark.setting_ids(["GL-SET-_unsigned-config-efi-binary-exists"])
@pytest.mark.feature("_unsigned")
@pytest.mark.arch("arm64")
def test_unsigned_efi_binary_exists_arm64(file):
    """Test that unsigned EFI binary exists for arm64"""
    assert file.is_regular_file("/boot/efi/EFI/BOOT/BOOTAA64.EFI")


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
    ], f"Clamav cron job should contain the correct content"
