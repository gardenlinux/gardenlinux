import pytest
from plugins.capabilities import Capabilities
from plugins.dpkg import Dpkg
from plugins.file import File
from plugins.find import Find
from plugins.parse_file import ParseFile
from plugins.shell import ShellRunner
from plugins.sysctl import Sysctl
from plugins.systemd import Systemd


@pytest.mark.feature("not container and not lima")
@pytest.mark.root(reason="required to verify directory permissions")
@pytest.mark.booted(reason="requires mounted filesystem inspection")
def test_tmp_exists(file: File):
    """
    As per DISA STIG requirement, the operating system must prevent program
    execution in accordance with local policies regarding software program usage.
    This test verifies that /tmp exists on the system.
    Ref: SRG-OS-000368-GPOS-00154
    """
    assert file.exists("/tmp"), "stigcompliance: /tmp does not exist"


@pytest.mark.feature("not container and not lima")
@pytest.mark.root(reason="required to verify directory permissions")
@pytest.mark.booted(reason="requires mounted filesystem inspection")
def test_tmp_is_directory(file: File):
    """
    As per DISA STIG requirement, the operating system must prevent program
    execution in accordance with local policies regarding software program usage.
    This test verifies that /tmp is a directory.
    Ref: SRG-OS-000368-GPOS-00154
    """
    assert file.is_dir("/tmp"), "stigcompliance: /tmp is not a directory"


@pytest.mark.feature("not container and not lima")
@pytest.mark.root(reason="required to verify directory permissions")
@pytest.mark.booted(reason="requires mounted filesystem inspection")
def test_tmp_has_sticky_bit(file: File):
    """
    As per DISA STIG requirement, the operating system must prevent program
    execution in accordance with local policies regarding software program usage.
    This test verifies that /tmp is world-writable with sticky bit set.
    Ref: SRG-OS-000368-GPOS-00154
    """
    assert file.has_permissions(
        "/tmp", "rwxrwxrwt"
    ), f"stigcompliance: /tmp is not world-writable with sticky bit (got {file.get_mode('/tmp')})"


@pytest.mark.feature("not container and not lima")
@pytest.mark.root(reason="required to verify directory permissions")
@pytest.mark.booted(reason="requires mounted filesystem inspection")
def test_var_tmp_exists(file: File):
    """
    As per DISA STIG requirement, the operating system must prevent program
    execution in accordance with local policies regarding software program usage.
    This test verifies that /var/tmp exists on the system.
    Ref: SRG-OS-000368-GPOS-00154
    """
    assert file.exists("/var/tmp"), "stigcompliance: /var/tmp does not exist"


@pytest.mark.feature("not container and not lima")
@pytest.mark.root(reason="required to verify directory permissions")
@pytest.mark.booted(reason="requires mounted filesystem inspection")
def test_var_tmp_is_directory(file: File):
    """
    As per DISA STIG requirement, the operating system must prevent program
    execution in accordance with local policies regarding software program usage.
    This test verifies that /var/tmp is a directory.
    Ref: SRG-OS-000368-GPOS-00154
    """
    assert file.is_dir("/var/tmp"), "stigcompliance: /var/tmp is not a directory"


@pytest.mark.feature("not container and not lima")
@pytest.mark.root(reason="required to verify directory permissions")
@pytest.mark.booted(reason="requires mounted filesystem inspection")
def test_var_tmp_has_sticky_bit(file: File):
    """
    As per DISA STIG requirement, the operating system must prevent program
    execution in accordance with local policies regarding software program usage.
    This test verifies that /var/tmp is world-writable with sticky bit set.
    Ref: SRG-OS-000368-GPOS-00154
    """
    assert file.has_permissions(
        "/var/tmp", "rwxrwxrwt"
    ), f"stigcompliance: /var/tmp is not world-writable with sticky bit (got {file.get_mode('/var/tmp')})"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires mounted filesystem inspection")
@pytest.mark.root(reason="required to verify execution restrictions")
def test_tmp_mount_exists(parse_file: ParseFile):
    """
    As per DISA STIG requirement, the operating system must prevent program
    execution in accordance with local policies regarding software program usage.
    This test verifies that /tmp has a mount entry in /proc/mounts.
    Ref: SRG-OS-000368-GPOS-00154
    """
    lines = parse_file.lines("/proc/mounts", format="spacedelim")
    assert any(
        "/tmp" in str(line) for line in lines
    ), "stigcompliance: /tmp mount entry not found in /proc/mounts"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires mounted filesystem inspection")
@pytest.mark.root(reason="required to verify execution restrictions")
def test_tmp_mounted_noexec(parse_file: ParseFile):
    """
    As per DISA STIG requirement, the operating system must prevent program
    execution in accordance with local policies regarding software program usage.
    This test verifies that /tmp is mounted with noexec in /proc/mounts.
    Ref: SRG-OS-000368-GPOS-00154
    """
    lines = parse_file.lines("/proc/mounts", format="spacedelim")
    assert any(
        "/tmp" in str(line) and "noexec" in str(line) for line in lines
    ), "stigcompliance: /tmp is not mounted with noexec"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires mounted filesystem inspection")
@pytest.mark.root(reason="required to verify execution restrictions")
def test_var_tmp_mount_exists(parse_file: ParseFile):
    """
    As per DISA STIG requirement, the operating system must prevent program
    execution in accordance with local policies regarding software program usage.
    This test verifies that /var/tmp has a mount entry in /proc/mounts.
    Ref: SRG-OS-000368-GPOS-00154
    """
    lines = parse_file.lines("/proc/mounts", format="spacedelim")
    assert any(
        "/var/tmp" in str(line) for line in lines
    ), "stigcompliance: /var/tmp mount entry not found in /proc/mounts"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires mounted filesystem inspection")
@pytest.mark.root(reason="required to verify execution restrictions")
def test_var_tmp_mounted_noexec(parse_file: ParseFile):
    """
    As per DISA STIG requirement, the operating system must prevent program
    execution in accordance with local policies regarding software program usage.
    This test verifies that /var/tmp is mounted with noexec in /proc/mounts.
    Ref: SRG-OS-000368-GPOS-00154
    """
    lines = parse_file.lines("/proc/mounts", format="spacedelim")
    assert any(
        "/var/tmp" in str(line) and "noexec" in str(line) for line in lines
    ), "stigcompliance: /var/tmp is not mounted with noexec"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires LSM subsystem")
@pytest.mark.root(reason="required to read kernel security state")
def test_lsm_execution_control_present(lsm):
    """
    As per DISA STIG requirement, the operating system must prevent program
    execution in accordance with local policies regarding software program usage.
    This test verifies that a Linux Security Module capable of enforcing
    execution control (AppArmor or SELinux) is active on the system.
    Ref: SRG-OS-000368-GPOS-00154
    """
    enforcement_lsms = {"apparmor", "selinux"}
    assert enforcement_lsms.intersection(set(lsm)), (
        f"stigcompliance: no execution-control LSM (AppArmor or SELinux) is active — "
        f"active LSMs: {lsm}"
    )


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires LSM subsystem")
@pytest.mark.root(reason="required to check AppArmor enforcement status")
def test_apparmor_is_active(systemd: Systemd, dpkg: Dpkg):
    """
    As per DISA STIG requirement, the operating system must prevent program
    execution in accordance with local policies regarding software program usage.
    This test verifies that the AppArmor service is active on the system.
    Ref: SRG-OS-000368-GPOS-00154
    """
    if not dpkg.package_is_installed("apparmor"):
        pytest.skip("AppArmor not installed — skipping enforcement check")

    assert systemd.is_active(
        "apparmor"
    ), "stigcompliance: AppArmor is installed but the apparmor service is not active"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires LSM subsystem")
@pytest.mark.root(reason="required to check AppArmor enforcement status")
def test_apparmor_is_enabled(systemd: Systemd, dpkg: Dpkg):
    """
    As per DISA STIG requirement, the operating system must prevent program
    execution in accordance with local policies regarding software program usage.
    This test verifies that the AppArmor service is enabled to survive reboots.
    Ref: SRG-OS-000368-GPOS-00154
    """
    if not dpkg.package_is_installed("apparmor"):
        pytest.skip("AppArmor not installed — skipping enforcement check")

    assert systemd.is_enabled(
        "apparmor"
    ), "stigcompliance: AppArmor is installed but the apparmor service is not enabled"


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires LSM subsystem")
@pytest.mark.root(reason="required to check AppArmor enforcement status")
def test_apparmor_has_enforce_mode_profiles(shell: ShellRunner, dpkg: Dpkg):
    """
    As per DISA STIG requirement, the operating system must prevent program
    execution in accordance with local policies regarding software program usage.
    This test verifies that AppArmor has profiles loaded in enforce mode
    so that execution policies are actively enforced.
    Ref: SRG-OS-000368-GPOS-00154
    """
    if not dpkg.package_is_installed("apparmor"):
        pytest.skip("AppArmor not installed — skipping enforcement check")

    status = shell("apparmor_status", capture_output=True, ignore_exit_code=True)
    assert (
        "enforce mode" in status.stdout
        or "profiles are in enforce mode" in status.stdout
    ), (
        "stigcompliance: AppArmor has no profiles in enforce mode — "
        "program execution policies are not being enforced"
    )


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires mounted filesystem")
@pytest.mark.root(reason="required to inspect filesystem for executable files")
def test_no_executable_files_in_tmp(find: Find, file: File):
    """
    As per DISA STIG requirement, the operating system must prevent program
    execution in accordance with local policies regarding software program usage.
    This test scans /tmp for executable files, which should not be present
    on a properly hardened system with noexec enforcement.
    Ref: SRG-OS-000368-GPOS-00154
    """
    find.same_mnt_only = True
    find.root_paths = ["/tmp"]
    find.entry_type = "files"

    executables = [f for f in find if file.is_executable(f)]

    assert (
        not executables
    ), "stigcompliance: executable files found in /tmp: " + ", ".join(executables)


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires mounted filesystem")
@pytest.mark.root(reason="required to inspect filesystem for executable files")
def test_no_executable_files_in_var_tmp(find: Find, file: File):
    """
    As per DISA STIG requirement, the operating system must prevent program
    execution in accordance with local policies regarding software program usage.
    This test scans /var/tmp for executable files, which should not be present
    on a properly hardened system with noexec enforcement.
    Ref: SRG-OS-000368-GPOS-00154
    """
    find.same_mnt_only = True
    find.root_paths = ["/var/tmp"]
    find.entry_type = "files"

    executables = [f for f in find if file.is_executable(f)]

    assert (
        not executables
    ), "stigcompliance: executable files found in /var/tmp: " + ", ".join(executables)


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires /proc/sys kernel parameters")
@pytest.mark.root(reason="required to read kernel sysctl parameters")
def test_aslr_enabled(sysctl: Sysctl):
    """
    As per DISA STIG requirement, the operating system must prevent program
    execution in accordance with local policies regarding software program usage.
    This test verifies that Address Space Layout Randomization (ASLR) is fully
    enabled (kernel.randomize_va_space=2) to prevent exploitation of executed
    programs through memory layout prediction.
    Ref: SRG-OS-000368-GPOS-00154
    """
    assert sysctl["kernel.randomize_va_space"] == 2, (
        f"stigcompliance: ASLR is not fully enabled — "
        f"kernel.randomize_va_space={sysctl['kernel.randomize_va_space']} (expected 2)"
    )


@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="requires mounted filesystem")
@pytest.mark.root(reason="required to inspect file capabilities")
def test_no_capabilities_on_files_in_tmp(capabilities: Capabilities):
    """
    As per DISA STIG requirement, the operating system must prevent program
    execution in accordance with local policies regarding software program usage.
    This test verifies that no files in /tmp have elevated Linux capabilities
    set, which could allow bypassing execution control policies.
    Ref: SRG-OS-000368-GPOS-00154
    """
    tmp_caps = [entry for entry in capabilities.get() if entry.startswith("/tmp/")]

    assert (
        not tmp_caps
    ), "stigcompliance: files in /tmp have elevated capabilities: " + ", ".join(
        tmp_caps
    )
