import os

import pytest
from plugins.file import File


@pytest.mark.feature("_fips")
def test_gnutls_fips_file_was_created(file: File):
    """
    GnuTLS requires to have the /etc/system-fips to be present as prerequisite
    to enable the FIPS mode.

    https://www.gnutls.org/manual/html_node/FIPS140_002d2-mode.html
    """

    assert file.is_file("/etc/system-fips")


@pytest.mark.feature("_fips")
def test_gnutls_fips_file_is_empty(file: File):
    """
    The /etc/system-fips should be without any content.
    """
    assert file.get_size("/etc/system-fips") == 0, f"The /etc/system-fips is not empty."


@pytest.mark.feature("_fips")
def test_libgcrypt_fips_file_was_created(file: File):
    """
    Libcgrypt requires to have the /etc/gcrypt/fips_enabled to be present as prerequisite
    to enable the FIPS mode.

    https://www.gnupg.org/documentation/manuals/gcrypt/Enabling-FIPS-mode.html
    """
    assert file.is_file("/etc/gcrypt/fips_enabled")


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
    assert file.is_file("/etc/kernel/cmdline.d/30-fips.cfg")


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
