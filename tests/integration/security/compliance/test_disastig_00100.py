"""
Ref: SRG-OS-000259-GPOS-00100

Verify the operating system limits privileges to change software resident
within software libraries.
"""

import fileinput
import glob
import platform

import pytest


ALLOWED_LIB_DIRS = {
    "x86_64": {
        "/usr/lib",
        "/usr/local/lib",
        "/lib/x86_64-linux-gnu",
        "/usr/lib/x86_64-linux-gnu",
        "/lib/i686-linux-gnu",
        "/lib32",
        "/usr/lib/i386-linux-gnu",
        "/usr/lib/i686-linux-gnu",
        "/usr/lib/x86_64-linux-gnu/libfakeroot",
        "/usr/lib32",
        "/usr/local/lib/i386-linux-gnu",
        "/usr/local/lib/i686-linux-gnu",
        "/usr/local/lib/x86_64-linux-gnu",
    },
    "aarch64": {
        "/usr/lib",
        "/usr/local/lib",
        "/usr/lib/aarch64-linux-gnu",
        "/usr/local/lib/aarch64-linux-gnu",
    },
}


@pytest.fixture
def ld_library_paths():
    return {
        line.strip()
        for line in fileinput.input(
            files=["/etc/ld.so.conf"] + glob.glob("/etc/ld.so.conf.d/*")
        )
        if line.strip().startswith("/")
    }


@pytest.mark.security_id(203675)
def test_no_unsolicited_lib_path_for_ldconfig(ld_library_paths):
    """Verify /etc/ld.so.conf and /etc/ld.so.conf.d/* contain only the architecture's allow-listed library paths."""
    diff = ld_library_paths - ALLOWED_LIB_DIRS[platform.machine()]
    assert not diff, f"unexpected shared libraries lookup paths configured: {diff}"


@pytest.mark.security_id(203675)
@pytest.mark.feature("disaSTIGmedium")
def test_lib_directories_are_only_root_writable(ld_library_paths, file):
    """Verify each ld.so library directory is root:root with mode rwxr-xr-x."""
    for lib_path in ld_library_paths:
        if file.exists(lib_path):
            assert file.get_owner(lib_path) == ("root", "root")
            assert file.has_permissions(lib_path, "rwxr-xr-x")


@pytest.mark.security_id(203675)
@pytest.mark.feature("disaSTIGmedium")
def test_python_lib_directory_is_only_root_writable(file, dpkg):
    """Verify /usr/lib/python3/dist-packages is root:root with mode rwxr-xr-x."""
    python_pkg = dpkg.collect_installed_packages().get_package("python3")
    if python_pkg:
        dist_packages = "/usr/lib/python3/dist-packages"
        assert file.get_owner(dist_packages) == ("root", "root")
        assert file.has_permissions(dist_packages, "rwxr-xr-x")


@pytest.mark.security_id(203675)
def test_python_disallows_installing_packages_with_pip_on_system_level(dpkg, file):
    """Verify /usr/lib/pythonX.Y/EXTERNALLY-MANAGED exists for the installed python3 version."""
    python_pkg = dpkg.collect_installed_packages().get_package("python3")
    if python_pkg:
        python_major_minor_ver = ".".join(python_pkg["Version"].split(".")[:2])
        assert file.exists(
            f"/usr/lib/python{python_major_minor_ver}/EXTERNALLY-MANAGED"
        )


@pytest.mark.security_id(203675)
def test_only_root_can_install_deb_packages(file):
    """Verify /var/lib/dpkg is root:root with mode rwxr-xr-x."""
    assert file.get_owner("/var/lib/dpkg") == ("root", "root")
    assert file.has_permissions("/var/lib/dpkg", "rwxr-xr-x")
