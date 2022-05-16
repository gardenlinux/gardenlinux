from helper.tests.key_val_in_file import key_val_in_file

def test_reset_env_vars(client):
    key_val_in_file(client, "/etc/sudoers", {"Defaults": "env_reset"},
                    invert=False, ignore_missing=False)