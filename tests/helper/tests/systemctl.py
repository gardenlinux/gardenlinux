def systemctl(client, state, services):
    """Test to check if systemd services are enabled or disabled as desired"""
    (exit_code, output, error) = client.execute_command(
            "systemctl list-unit-files", quiet=True)
    assert exit_code == 0, f"no {error=} expected"

    enabled = _return_services(output, ["enabled", "static"])
    disabled = _return_services(output, ["disabled"])

    # get list of enabled systemd services
    if state == "enabled":
        missing_enabled = _check_missing(enabled, services)
        assert len(missing_enabled) == 0, (f"{', '.join(missing_enabled)} are " +
                "not enabled as expected")

    # get list of disabled systemd services
    if state == "disabled":
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

def _return_services(services, states):
    out =[]
    for service in services.splitlines():
        for state in states:
            if state in service:
                out.append(service.split(' ', 1)[0])
    return out
