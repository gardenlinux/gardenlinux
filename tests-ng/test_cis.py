import pytest


@pytest.mark.feature("cis")
@pytest.mark.root(reason="CIS audit requires root privileges")
@pytest.mark.booted(reason="Must be run on a booted system")
def test_debian_cis_audit(shell):
    """
    Run the Debian CIS audit script and fail if any check shows 'KO'.
    """
    shell("sysctl -w net.ipv6.conf.lo.disable_ipv6=0", ignore_exit_code=True)

    shell(
        "sed -i 's|^status=audit|status=disabled|' "
        "/opt/cis-hardening/etc/conf.d/disable_source_routed_packets.cfg",
        ignore_exit_code=True,
    )

    result = shell(
        "/opt/cis-hardening/bin/hardening.sh --audit --allow-unsupported-distribution",
        capture_output=True,
        ignore_exit_code=True,
    )

    output = result.stdout + result.stderr

    failed_lines = [
        line.strip()
        for line in output.splitlines()
        if " KO " in line or line.strip().endswith("KO")
    ]

    if failed_lines:
        summary = "\n".join(f"FAILED {line}" for line in failed_lines)
        pytest.fail(f"\nCIS audit found {len(failed_lines)} failing checks:\n{summary}")

    assert "Check Failed" not in output, "CIS audit run itself failed unexpectedly"
