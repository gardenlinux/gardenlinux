import pytest
from plugins.shell import ShellRunner

@pytest.mark.feature("cis")
@pytest.mark.root(reason="CIS audit requires root privileges")
@pytest.mark.booted(reason="CIS tests within a booted system")
@pytest.mark.modify(reason="CIS audit script marked for modifying")
def test_debian_cis_audit(shell):
    """
    Run the Debian CIS audit script and fail if any check shows 'KO'.
    """
    result = shell(
        "/opt/cis-hardening/bin/hardening.sh --audit --allow-unsupported-distribution",
        capture_output=True,
        ignore_exit_code=True,
    )

    output = result.stdout + result.stderr

    # Correct condition grouping:
    #   - Match lines with KO
    #   - Exclude any line containing "Check Failed"
    failed_lines = [
        line.strip()
        for line in output.splitlines()
        if ("Check Failed" not in line)
        and (" KO " in line or line.strip().endswith("KO"))
    ]

    # Remove duplicate lines (same test printed twice)
    unique_failed = sorted(set(failed_lines))

    if unique_failed:
        summary = "\n".join(f"FAILED {line}" for line in unique_failed)
        raise AssertionError(f"{len(unique_failed)} CIS check(s) failed:\n{summary}")

    # Ensure CIS script itself didn't fail
    assert "Check Failed" not in output, "CIS audit run itself failed unexpectedly"


@pytest.mark.root(reason="CIS audit requires root privileges")
@pytest.mark.booted(reason="CIS tests within a booted system")
def test_umask_cmd(shell: ShellRunner):
    result = shell("su --login --command 'umask'", capture_output=True)
    assert result.returncode == 0, f"Could not execute umask cmd: {result.stderr}"
    assert result.stdout == "0077\n", "umask is not set to 0077"
