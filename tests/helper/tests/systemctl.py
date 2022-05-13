def systemctl(client, state, services):
    """Test to check if systemd services are enabled or disabled as desired"""
    # get list of enabled systemd services
    if state == "enabled":
        (exit_code, output, error) = client.execute_command(
            "systemctl list-unit-files | awk '$2~/static/ { print $1; " +
            "next} $2~/enabled/ { print $1; next; }'", quiet=True)
        assert exit_code == 0, f"no {error=} expected"
        enabled = output
        missing_enabled = _check_missing(enabled, services)
        assert len(missing_enabled) == 0, (f"{', '.join(missing_enabled)} are " +
                "not enabled as expected")

    # get list of disabled systemd services
    if state == "disabled":
        (exit_code, output, error) = client.execute_command(
            "systemctl list-unit-files | awk '$2~/disabled/ { print $1; " +
            "next}'", quiet=True)
        assert exit_code == 0, f"no {error=} expected"
        disabled = output
        missing_disabled = _check_missing(disabled, services)
        assert len(missing_disabled) == 0, (f"{', '.join(missing_disabled)} are " +
                "not disabled as expected")


def _check_missing(configured, expected):
    """Check if an item of the expected list is in configured, returns a list
    containing the items not found"""
    missing = []
    for item in expected:
        if not item in configured:
            missing.append(item)
    return missing
