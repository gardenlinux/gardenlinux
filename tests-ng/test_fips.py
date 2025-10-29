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
