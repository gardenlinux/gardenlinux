import os
import pytest

from stat import S_ISREG

def test_gnutls_fips_file_was_created():
    """
    GnuTLS requieres to have the /etc/system-fips to be present as prerequisite 
    to enable the FIPS mode.

    https://www.gnutls.org/manual/html_node/FIPS140_002d2-mode.html
    """
    gnutls_fips_file = os.stat("/etc/system-fips")
    gnutls_fips_file_state = S_ISREG(gnutls_fips_file.st_mode)

    assert gnutls_fips_file, f"The /etc/system-fips file does not exist."


def test_gnutls_fips_file_is_empty():
    """
    The /etc/system-fips should be without any content.
    """
    gnutls_fips_file = os.stat("/etc/system-fips")

    assert gnutls_fips_file.st_size == 0, f"The /etc/system-fips is not empty."


def test_libgcrypt_fips_file_was_created():
    """
    Libcgrypt requieres to have the /etc/gcrypt/fips_enabled to be present as prerequisite 
    to enable the FIPS mode.

    https://www.gnupg.org/documentation/manuals/gcrypt/Enabling-FIPS-mode.html
    """
    libgcrypt_fips_file = os.stat("/etc/gcrypt/fips_enabled")
    libgcrypt_fips_file_state = S_ISREG(libgcrypt_fips_file.st_mode)

    assert libgcrypt_fips_file_state, f"The /etc/system-fips file does not exist."


def test_libgcrypt_fips_file_is_empty():
    """
    The /etc/gcrypt/fips_enabled should be without any content.
    """
    gnutls_fips_file = os.stat("/etc/gcrypt/fips_enabled")

    assert gnutls_fips_file.st_size == 0, f"The /etc/gcrypt/fips_enabled is not empty."
