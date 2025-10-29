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


def test_kernel_cmdline_fips_file_was_created():
    """
    libgcrypt, gnutls and openssl need to have the /proc/sys/crypto/fips_enabled present
    as a prerequisite to enable they respected FIPS mode. The kernel can only be booted
    with the fips=1 paraemter. 
    """
    kernel_fips_file = os.stat("/etc/kernel/cmdline.d/30-fips.cfg")
    kernel_fips_file_state = S_ISREG(kernel_fips_file.st_mode)

    assert kernel_fips_file_state, f"The /etc/kernel/cmdline.d/30-fips.cfg is missing!"


def test_kernel_cmdline_fips_file_content():
    """
    We have to ensure that the fips=1 was set. 
    """
    with open("/etc/kernel/cmdline.d/30-fips.cfg") as kernel_cmd_file:
        assert kernel_cmd_file.read() == 'CMDLINE_LINUX="$CMDLINE_LINUX fips=1"\n', "fips=1 wasn't set in the kernel cmdline"


@pytest.mark.booted(reason="Kernel test makes sense only on booted system")
def test_kernel_was_boot_with_fips_mode():
    """
    Validate that the kernel was booted with the FIPS mode enabled. 
    """
    with open("/proc/sys/crypto/fips_enabled", "r") as f:
        fips_enabled = f.read().strip()
    assert fips_enabled == "1", f"Kernel is not in fips mode!"
