import pytest
from plugins.file import File
from plugins.systemd import Systemd

# =============================================================================
# _usi Feature
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-_usi-config-kernel-cmdline-no-gpt-auto"
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
        "/etc/kernel/cmdline.d/99-no-gpt-auto.cfg",
        "/etc/update-motd.d/25-secureboot",
        "/usr/local/sbin/update-kernel-cmdline",
        "/usr/sbin/enroll-gardenlinux-secureboot-keys",
    ]

    missing = [path for path in paths if not file.exists(path)]
    assert not missing, f"The following files were not found: {', '.join(missing)}"


# =============================================================================
# cisModprobe Feature
# =============================================================================


@pytest.mark.setting_ids([
    "GL-SET-cisModprobe-config-modprobe-cramfs"
    "GL-SET-cisModprobe-config-modprobe-dccp"
    "GL-SET-cisModprobe-config-modprobe-freevxfs"
    "GL-SET-cisModprobe-config-modprobe-jffs2"
    "GL-SET-cisModprobe-config-modprobe-rds"
    "GL-SET-cisModprobe-config-modprobe-sctp"
    "GL-SET-cisModprobe-config-modprobe-squashfs"
    "GL-SET-cisModprobe-config-modprobe-tipc"
    "GL-SET-cisModprobe-config-modprobe-udf"
    ])
@pytest.mark.feature("cisModprobe")
def test_cismodprobe_blacklist_exists(file: File):
    """Test that kernel modules are blacklisted"""
    paths = [
        "/etc/modprobe.d/cramfs.conf",
        "/etc/modprobe.d/dccp.conf",
        "/etc/modprobe.d/freevxfs.conf",
        "/etc/modprobe.d/jffs2.conf",
        "/etc/modprobe.d/rds.conf",
        "/etc/modprobe.d/sctp.conf",
        "/etc/modprobe.d/squashfs.conf",
        "/etc/modprobe.d/tipc.conf",
        "/etc/modprobe.d/udf.conf",
    ]

    missing = [path for path in paths if not file.exists(path)]
    assert not missing, f"The following files were not found: {', '.join(missing)}"

@pytest.mark.setting_ids([
    "GL-SET-cisModprobe-config-modprobe-cramfs"
    "GL-SET-cisModprobe-config-modprobe-dccp"
    "GL-SET-cisModprobe-config-modprobe-freevxfs"
    "GL-SET-cisModprobe-config-modprobe-jffs2"
    "GL-SET-cisModprobe-config-modprobe-rds"
    "GL-SET-cisModprobe-config-modprobe-sctp"
    "GL-SET-cisModprobe-config-modprobe-squashfs"
    "GL-SET-cisModprobe-config-modprobe-tipc"
    "GL-SET-cisModprobe-config-modprobe-udf"
    ])
@pytest.mark.feature("cisModprobe")
def test_cismodprobe_modules_not_loaded(modprobe: Modprobe):
    """Test that modules are not loaded"""
    modules = [
        "cramfs",
        "dccp",
        "freevxfs",
        "jffs2",
        "rds",
        "sctp",
        "squashfs",
        "tipc",
        "udf",
    ]

    for module in modules:
        assert not modprobe.is_module_loaded(module), f"Module {module} is loaded but should be deny listed"


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
    missing = [parameter.split("=")[0] for parameter in parameters if parameter.split("=")[0] not in sysctl]
    assert not missing, f"The following parameters were not set to the expected value: {', '.join(missing)}"

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
