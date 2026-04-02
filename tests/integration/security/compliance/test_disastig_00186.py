import pytest


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="requires running network stack")
@pytest.mark.root(reason="requires access to sysctl parameters")
def test_icmp_rate_limiting_enabled(sysctl):
    """
    As per DISA STIG compliance requirements, the operating system must protect against or
    limit the effects of Denial of Service (DoS) attacks by ensuring the operating
    system is implementing rate-limiting measures on impacted network interfaces.
    Ref: RG-OS-000420-GPOS-00186
    """
    value = sysctl["net.ipv4.icmp_ratelimit"]

    assert (
        isinstance(value, int) and value > 0
    ), f"stigcompliance: ICMP rate limiting not enabled (value={value})"


@pytest.mark.feature("not container")
@pytest.mark.booted(reason="requires network stack")
@pytest.mark.root(reason="requires access to sysctl parameters")
def test_tcp_syncookies_enabled(sysctl):
    """
    As per DISA STIG compliance requirements, the operating system must protect against or
    limit the effects of Denial of Service (DoS) attacks by ensuring the operating
    system is implementing rate-limiting measures on impacted network interfaces.
    Ref: RG-OS-000420-GPOS-00186
    """
    value = sysctl["net.ipv4.tcp_syncookies"]

    assert value == 1, f"stigcompliance: tcp_syncookies not enabled (value={value})"
