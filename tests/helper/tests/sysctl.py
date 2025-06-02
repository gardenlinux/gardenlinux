import logging
import pytest

logger = logging.getLogger(__name__)


def check_sysctl(client, key, operator, value):
    (exit_code, output, error) = client.execute_command(
        "sudo -u root /usr/sbin/sysctl -a", quiet=True
    )
    assert exit_code == 0, f"no {error=} expected"

    sysctls = {}
    for line in output:
        if len(line) < 1 or line.startswith("#"):
            continue
        s = line.split("=", 1)
        if len(s) < 2:
            continue
        sysctls[s[0].strip()] = s[1].strip()

    match operator:
        case "is":
            assert key in sysctls
            assert sysctls[key] == value, f"{key} is not {value} but {sysctls[key]}"
        case "isnot":
            assert key in sysctls
            assert sysctls[key] != value, f"{key} should not be {value}"
        case "isnotornotset":
            if key in sysctls:
                assert (
                    sysctls[key] != value
                ), f"as {key} is set, it should not be {value}"
        case "isset":
            assert key in sysctls, f"{key} should be set"
        case "isnotset":
            assert key not in sysctls, f"{key} should not be set"
        case _:
            pytest.fail(f"unsupported operator {operator}")
