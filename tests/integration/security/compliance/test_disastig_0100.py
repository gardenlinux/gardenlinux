import fileinput
import glob

import pytest

"""
Ref: SRG-OS-000259-GPOS-00100

Verify the operating system limits privileges to change software resident
within software libraries.
"""


ALLOWED_LIB_DIRS = {
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


def test_no_unsolicited_lib_path_for_ldconfig(ld_library_paths):
    diff = ld_library_paths - ALLOWED_LIB_DIRS
    assert not diff, f"unexpected shared libraries lookup paths configured: {diff}"


def test_lib_directories_are_only_root_writable(ld_library_paths, file):
    for lib_path in ld_library_paths:
        if file.exists(lib_path):
            assert file.get_owner(lib_path) == ("root", "root")
            assert file.has_permissions(lib_path, "rwxr-xr-x")


def test_python_lib_directory_is_only_root_writable(file):
    dist_packages = "/usr/lib/python3/dist-packages"
    assert file.get_owner(dist_packages) == ("root", "root")
    assert file.has_permissions(dist_packages, "rwxr-xr-x")


def test_python_disallows_installing_packages_with_pip_on_system_level(dpkg, file):
    python_pkg = dpkg.collect_installed_packages().get_package("python3")
    if python_pkg:
        python_major_minor_ver = ".".join(python_pkg["Version"].split(".")[:2])
        assert file.exists(
            f"/usr/lib/python{python_major_minor_ver}/EXTERNALLY-MANAGED"
        )


def test_only_root_can_install_deb_packages(file):
    assert file.get_owner("/var/lib/dpkg") == ("root", "root")
    assert file.has_permissions("/var/lib/dpkg", "rwxr-xr-x")
