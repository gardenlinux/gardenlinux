import configparser
import hmac
import os
from ctypes import CDLL
from ctypes.util import find_library
from hashlib import _hashlib  # type: ignore
from hashlib import md5 as MD5
from hashlib import sha1 as SHA1
from hashlib import sha256 as SHA256
from platform import machine as arch
from typing import List

import pytest
from plugins.file import File
from plugins.kernel_cmdline import kernel_cmdline
from plugins.parse_file import ParseFile


@pytest.mark.feature("_fips")
def test_gnutls_fips_file_was_created(file: File):
    """
    GnuTLS requires to have the /etc/system-fips to be present as prerequisite
    to enable the FIPS mode.

    https://www.gnutls.org/manual/html_node/FIPS140_002d2-mode.html
    """

    assert file.is_regular_file("/etc/system-fips")


@pytest.mark.feature("_fips")
def test_gnutls_fips_file_is_empty(file: File):
    """
    The /etc/system-fips should be without any content.
    """
    assert file.get_size("/etc/system-fips") == 0, f"The /etc/system-fips is not empty."


@pytest.mark.feature("_fips")
def test_gnutls_is_in_fips_mode():
    """
    This code will call up the GnuTLS library directly with ctypes.
    It invokes the gnutls_fips140_mode_enabled to return true when the library is in FIPS mode;
    It will return a C-type true.

    https://www.gnutls.org/manual/html_node/FIPS140_002d2-mode.html
    https://manpages.debian.org/testing/gnutls-doc/gnutls_fips140_mode_enabled.3.en.html

    """
    shared_lib_name = find_library("gnutls")
    gnutls = CDLL(shared_lib_name)
    assert gnutls.gnutls_fips140_mode_enabled(), "Error GnuTLS can't be started in FIPS mode."


@pytest.mark.feature("_fips")
def test_gnutls_fips_dot_hmac_file_is_presented():
    """
    GnuTLS will perform a self check based on the FIPS requirements. A file that
    contains an HMAC needs to be present on the target system. This test ensures
    that the file was installed.

    https://www.gnutls.org/manual/html_node/FIPS140_002d2-mode.html
    """
    gnutls_fips_hmac_file = f"/usr/lib/{arch()}-linux-gnu/.libgnutls.so.30.hmac"
    assert os.path.isfile(
        gnutls_fips_hmac_file
    ), f"The f{gnutls_fips_hmac_file} file does not exist!"


@pytest.mark.feature("_fips")
def test_gnutls_fips_dot_hmac_file_is_vaild():
    """
    One problem in shipping GnuTLS packages was that the computed HMAC was not valid for the shipped
    version of the library since the HMAC was computed for an unstripped version. This test ensures
    that the HMAC on the system fits with the shipped library version.

    Without the HMAC the selftest will fail at second part with the follow error message:

    |<1>| FIPS140-2 self testing part 2 failed

    """
    gnutls_lib_path = f"/usr/lib/{arch()}-linux-gnu/libgnutls.so.30"
    gnutls_fips_hmac_file = f"/usr/lib/{arch()}-linux-gnu/.libgnutls.so.30.hmac"
    # https://gitlab.com/gnutls/gnutls/-/blob/master/configure.ac?ref_type=heads#L677
    SECRET = "orboDeJITITejsirpADONivirpUkvarP"

    config = configparser.ConfigParser()
    config.read(gnutls_fips_hmac_file)

    fips_hmac = hmac.new(key=SECRET.encode("UTF-8"), msg=None, digestmod=SHA256)
    # Need to read it 'b' since it's a binary file.
    with open(gnutls_lib_path, mode="rb") as lib:
        fips_hmac.update(lib.read())

    assert (
        config["libgnutls.so.30"]["hmac"] == fips_hmac.hexdigest()
    ), "Compute HMAC is incorrect!"


@pytest.mark.feature("_fips")
def test_libgcrypt_fips_file_was_created(file: File):
    """
    Libcgrypt requires to have the /etc/gcrypt/fips_enabled to be present as prerequisite
    to enable the FIPS mode.

    https://www.gnupg.org/documentation/manuals/gcrypt/Enabling-FIPS-mode.html
    """
    assert file.is_regular_file("/etc/gcrypt/fips_enabled")


@pytest.mark.feature("_fips")
def test_libgcrypt_fips_file_is_empty(file: File):
    """
    The /etc/gcrypt/fips_enabled should be without any content.
    """
    assert (
        file.get_size("/etc/gcrypt/fips_enabled") == 0
    ), f"The /etc/gcrypt/fips_enabled is not empty."


@pytest.mark.feature("_fips")
def test_kernel_cmdline_fips_file_was_created(file: File):
    """
    libgcrypt, gnutls and openssl need to have the /proc/sys/crypto/fips_enabled present
    as a prerequisite to enable they respected FIPS mode. The kernel can only be booted
    with the fips=1 parameter.
    """
    assert file.is_regular_file("/etc/kernel/cmdline.d/30-fips.cfg")


@pytest.mark.feature("_fips")
def test_kernel_cmdline_fips_file_content(parse_file: ParseFile):
    """
    We have to ensure that the fips=1 was set.
    """
    lines = parse_file.lines("/etc/kernel/cmdline.d/30-fips.cfg")
    assert 'CMDLINE_LINUX="$CMDLINE_LINUX fips=1"' in lines


@pytest.mark.feature("_fips")
@pytest.mark.booted(reason="Kernel test makes sense only on booted system")
def test_kernel_was_boot_with_fips_mode(kernel_cmdline: List[str]):
    """
    Validate that the kernel was booted with the FIPS mode enabled.
    """
    assert "fips=1" in kernel_cmdline, f"Kernel was not booted in FIPS mode!"


@pytest.mark.feature("_fips")
@pytest.mark.booted(reason="Kernel test makes sense only on booted system")
def test_kernel_has_fips_entry_in_procfs(parse_file: ParseFile):
    """
    Validate that the FIPS flag is exposed in procfs. Without applications can't detect if a system
    has been booted into FIPS mode.
    """
    lines = parse_file.lines("/proc/sys/crypto/fips_enabled")
    assert "1" in lines, f"Kernel was not booted in FIPS mode!"
