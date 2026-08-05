"""
Ref: SRG-OS-000725-GPOS-00180

Verify he operating system is configured to allow user selection of long
passwords and passphrases, including spaces and all printable characters for
password-based authentication.
"""

import glob
import re
from os.path import exists

import pytest


@pytest.mark.security_id(263655)
def test_password_length_is_not_limited_in_pam_configs():
    """Verify no PAM config caps password length via passwdqc max=."""
    search_str = r"^\s*password\s+requisite\s+pam_passwdqc.so\s+[^#]*max=\d+"
    pattern = re.compile(search_str)
    found = False

    for config in glob.glob("/etc/pam.d/*"):
        with open(config) as f:
            for line in f:
                if pattern.search(line):
                    found = True
                    offender = config
                    break
    assert not found, f"Password limit is set in {offender}"


@pytest.mark.security_id(263655)
def test_password_length_is_not_limited_in_passwdqc_config(parse_file):
    """Verify /etc/passwdqc.conf does not cap password length via max=."""
    config = "/etc/passwdqc.conf"
    if not exists(config):
        return
    assert "max" not in parse_file.parse(config)
