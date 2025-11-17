import configparser
import hmac
import os
from hashlib import _hashlib  # type: ignore
from hashlib import md5 as MD5
from hashlib import sha1 as SHA1
from hashlib import sha256 as SHA256
from platform import machine as arch
from stat import S_ISREG

import pytest


@pytest.mark.feature("_fips")
def test_gnutls_fips_file_was_created():
    """
    GnuTLS requires to have the /etc/system-fips to be present as prerequisite
    to enable the FIPS mode.

    https://www.gnutls.org/manual/html_node/FIPS140_002d2-mode.html
    """
    gnutls_fips_file = os.stat("/etc/system-fips")
    gnutls_fips_file_state = S_ISREG(gnutls_fips_file.st_mode)

    assert gnutls_fips_file, f"The /etc/system-fips file does not exist."


@pytest.mark.feature("_fips")
def test_gnutls_fips_file_is_empty():
    """
    The /etc/system-fips should be without any content.
    """
    gnutls_fips_file = os.stat("/etc/system-fips")

    assert gnutls_fips_file.st_size == 0, f"The /etc/system-fips is not empty."


@pytest.mark.feature("_fips")
def test_gnutls_fips_dot_hmac_file_is_presented():
    """
    GnuTLS will perform based on the FIPS requierment a self check. This requieres to have a
    file that contains a HMAC presented on the target system. This test ensure that the file
    was installed.

    https://www.gnutls.org/manual/html_node/FIPS140_002d2-mode.html
    """
    gnutls_fipshmac_path = f"/usr/lib/{arch()}-linux-gnu/.libgnutls.so.30.hmac"
    gnutls_fipshmac_file = os.stat(gnutls_fipshmac_path)
    gnutls_fipshmac_file_state = S_ISREG(gnutls_fipshmac_file.st_mode)

    assert (
        gnutls_fipshmac_file_state
    ), f"The f{gnutls_fipshmac_path} file does not exist."


@pytest.mark.feature("_fips")
def test_gnutls_fips_dot_hmac_file_is_vaild():
    """
    Key problem in shipping GnuTLS packages was that the computed HMAC was not vailded for the ship
    version of the library since the HMAC was computed for an unstripped version. This test ensures
    that the HMAC on the system fits with the shipped one.
    """
    ARCH = arch()
    gnutls_fipshmac_path = f"/usr/lib/{ARCH}-linux-gnu/.libgnutls.so.30.hmac"
    gnutls_lib_path = f"/usr/lib/{ARCH}-linux-gnu/libgnutls.so.30"
    # https://gitlab.com/gnutls/gnutls/-/blob/master/configure.ac?ref_type=heads#L677
    SECRET = "orboDeJITITejsirpADONivirpUkvarP"

    config = configparser.ConfigParser()
    config.read("/usr/lib/aarch64-linux-gnu/.libgnutls.so.30.hmac")

    fipshmac = hmac.new(key=SECRET.encode("UTF-8"), msg=None, digestmod=SHA256)
    # Need to read it 'b' since it's a binary file.
    with open(gnutls_lib_path, mode="rb") as lib:
        fipshmac.update(lib.read())

    assert (
        config["libgnutls.so.30"]["hmac"] == fipshmac.hexdigest()
    ), "Compute HMAC is incorrect!"


@pytest.mark.feature("_fips")
def test_gnutls_fips_dot_hmac_file_contains_vaild_hmac():
    """
    Test that the computed HMAC that was shipped is correct. Else the selftest will fail at the
    second
    """
    gnutls_fips_hmac_path = f"/usr/lib/{arch()}-linux-gnu/.libgnutls.so.30.hmac"

    config = configparser.ConfigParser()
    config.read("/usr/lib/aarch64-linux-gnu/.libgnutls.so.30.hmac")


@pytest.mark.feature("_fips")
def test_libgcrypt_fips_file_was_created():
    """
    Libcgrypt requires to have the /etc/gcrypt/fips_enabled to be present as prerequisite
    to enable the FIPS mode.

    https://www.gnupg.org/documentation/manuals/gcrypt/Enabling-FIPS-mode.html
    """
    libgcrypt_fips_file = os.stat("/etc/gcrypt/fips_enabled")
    libgcrypt_fips_file_state = S_ISREG(libgcrypt_fips_file.st_mode)

    assert libgcrypt_fips_file_state, f"The /etc/system-fips file does not exist."


@pytest.mark.feature("_fips")
def test_libgcrypt_fips_file_is_empty():
    """
    The /etc/gcrypt/fips_enabled should be without any content.
    """
    gnutls_fips_file = os.stat("/etc/gcrypt/fips_enabled")

    assert gnutls_fips_file.st_size == 0, f"The /etc/gcrypt/fips_enabled is not empty."


@pytest.mark.feature("_fips")
def test_kernel_cmdline_fips_file_was_created():
    """
    libgcrypt, gnutls and openssl need to have the /proc/sys/crypto/fips_enabled present
    as a prerequisite to enable they respected FIPS mode. The kernel can only be booted
    with the fips=1 parameter.
    """
    kernel_fips_file = os.stat("/etc/kernel/cmdline.d/30-fips.cfg")
    kernel_fips_file_state = S_ISREG(kernel_fips_file.st_mode)

    assert kernel_fips_file_state, f"The /etc/kernel/cmdline.d/30-fips.cfg is missing!"


@pytest.mark.feature("_fips")
def test_kernel_cmdline_fips_file_content():
    """
    We have to ensure that the fips=1 was set.
    """
    with open("/etc/kernel/cmdline.d/30-fips.cfg") as kernel_cmd_file:
        assert (
            kernel_cmd_file.read() == 'CMDLINE_LINUX="$CMDLINE_LINUX fips=1"\n'
        ), "fips=1 wasn't set in the kernel cmdline"


@pytest.mark.feature("_fips")
@pytest.mark.booted(reason="Kernel test makes sense only on booted system")
def test_kernel_was_boot_with_fips_mode():
    """
    Validate that the kernel was booted with the FIPS mode enabled.
    """
    with open("/proc/sys/crypto/fips_enabled", "r") as f:
        fips_enabled = f.read().strip()
    assert fips_enabled == "1", f"Kernel was not booted in FIPS mode!"
