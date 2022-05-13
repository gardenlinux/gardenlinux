def reset_env_vars(client):
    """Test for checking if sudoers defaults set env_reset"""
    (exit_code, _, _) = client.execute_command(
        f"grep '^Defaults.env_reset' /etc/sudoers", quiet=True)

    assert exit_code == 0, "For sudo the environment variables are not reset"