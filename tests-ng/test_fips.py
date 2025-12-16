import configparser
import hmac
import os
from ctypes import CDLL, c_int, c_void_p
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
@pytest.mark.booted("GnuTLS needs to have a VM booted with boot FIPS mode.")
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
    assert (
        gnutls.gnutls_fips140_mode_enabled()
    ), "Error GnuTLS can't be started in FIPS mode."


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
def test_that_openssl_has_fips_provider_is_presented(file: File):
    """
    We have to ensure that the fips.so is presented on the system.
    """
    assert file.is_regular_file(f"/usr/lib/{arch()}-linux-gnu/ossl-modules/fips.so")


@pytest.mark.feature("_fips")
def test_libssl_is_in_fips_mode():
    """
    We get OSSL_LIB_CTX_get0_global_default from libssl. For this we need to set up the correct
    return values

    First, we have to set up an OSSL_LIB_CTX; for this, we use OSSL_LIB_CTX_get0_global_default, which
    returns a C pointer.

    Once we have the global context, we can use this to get the default properties of the high-level
    algorithm that has been enabled. Similar to OSSL_LIB_CTX_get0_global_default, we need to define
    the expected return value. Since this is a C boolean, we have to set it to int, but we also have
    to define the argument type to be an array with a C pointer, since it is the pointer to the
    context object.
    """

    shared_lib_name = find_library("ssl")
    libssl = CDLL(shared_lib_name)

    libssl.OSSL_LIB_CTX_get0_global_default.restype = c_void_p
    libssl.OSSL_LIB_CTX_get0_global_default.argtypes = []
    libssl.EVP_default_properties_is_fips_enabled.restype = c_int
    libssl.EVP_default_properties_is_fips_enabled.argtypes = [c_void_p]

    ctx = libssl.OSSL_LIB_CTX_get0_global_default()
    assert libssl.EVP_default_properties_is_fips_enabled(
        ctx
    ), "Error openssl can't be started in FIPS mode."


def test_libgcrypt_is_in_fips_mode():
    """
     This will check if libgcrypt is in FIPS mode. There is no other way to call libgcrypt from
     Python than using ctypes.

    It might seem more reasonable to call the gcry_fips_mode_active, however, it turns out that this
    is a C preprocessor macro that can't be invoked by Python ctypes. Instead, we will invoke the
    following function, gcry_control(GCRYCTL_FIPS_MODE_P, 0) , which the macro will resolve as we.


    https://git.gnupg.org/cgi-bin/gitweb.cgi?p=libgcrypt.git;a=blob;f=src/gcrypt.h.in;h=712a8dd7931e76c0a83aee993bf22f34e420bfc2;hb=737cc63600146f196738a6768679eb016cf866e9#l2129

    The GCRYCTL_FIPS_MODE_P is again just a static value. That can be extract from the gcrypt.h
    headers.
    # https://git.gnupg.org/cgi-bin/gitweb.cgi?p=libgcrypt.git;a=blob;f=src/gcrypt.h.in;h=712a8dd7931e76c0a83aee993bf22f34e420bfc2;hb=737cc63600146f196738a6768679eb016cf866e9#l316
    The package libgcrypt20 needs to be presented.

    The gcry_control requires c type integer as inputs.

    https://www.gnupg.org/documentation/manuals/gcrypt/Enabling-FIPS-mode.html#Enabling-FIPS-mode
    https://www.gnupg.org/documentation/manuals/gcrypt/Controlling-the-library.html#index-gcry_005ffips_005fmode_005factive
    """
    shared_lib_name = find_library("gcrypt")
    libgcrypt = CDLL(shared_lib_name)

    # See the gcrypt.h
    GCRYCTL_FIPS_MODE_P = 55
    assert libgcrypt.gcry_control(
        c_int(GCRYCTL_FIPS_MODE_P), c_int(1)
    ), "Error libgcrypt can't be started in FIPS mode."


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
