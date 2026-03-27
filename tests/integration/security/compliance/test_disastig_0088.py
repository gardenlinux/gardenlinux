"""
Ref: SRG-OS-000228-GPOS-00088

Verify any publically accessible connection to the operating system displays
the Standard Mandatory DoD Notice and Consent Banner before granting access to
the system.
"""


def test_notice_and_consent_banner_is_presented_on_login(file):
    """You are accessing a U.S. Government (USG) Information System (IS) that is provided for USG-authorized use only."""
    assert file.icontains(
        "/etc/motd", "You are accessing SAP computer systems and network"
    )
    assert file.icontains("/etc/motd", "unauthorized access is prohibited")

    """The USG routinely intercepts and monitors communications on this IS"""
    """At any time, the USG may inspect and seize data stored on this IS"""
    assert file.icontains(
        "/etc/motd",
        "SAP has the right to scan and monitor access to and use of SAP Systems",
    )

    """Communications using, or data stored on, this IS are not private"""
    assert file.contains(
        "/etc/motd",
        "any information stored in, transmitted through or processed by SAP Systems remains at all times the property of SAP",
    )

    """This IS includes security measures (e.g., authentication and access controls) to protect USG interests--not for your personal benefit or privacy."""
    assert file.icontains(
        "/etc/motd",
        "you should have no expectation of privacy as to any information stored in, transmitted through or processed by any portion of SAP Systems",
    )
