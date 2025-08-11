import pytest
from .shell import ShellRunner


class Sshd:
    def __init__(self, shell: ShellRunner):
        sshd_config_test_command = shell("/usr/sbin/sshd -T", capture_output=True, ignore_exit_code=True)
        assert (
            sshd_config_test_command.returncode == 0
        ), f"Expected return code 0, got {sshd_config_test_command.returncode}"
        self._sshd_config = {}
        for line in sshd_config_test_command.stdout.splitlines():
            if not line.strip():
                continue
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                key, value = parts
                # If key already exists, convert to set and append
                if key in self._sshd_config:
                    if isinstance(self._sshd_config[key], set):
                        self._sshd_config[key].add(value)
                    else:
                        self._sshd_config[key] = {self._sshd_config[key], value}
                else:
                    # fixme: this is not ideal. what we want here is to have comma separated string values
                    # as a set to make comparing them easier because the order of entries does not matter
                    # the 3 is an arbitrary number to allow for real string values with commas
                    if value.count(",") >= 3:
                        self._sshd_config[key] = set(value.split(","))
                    else:
                        self._sshd_config[key] = value
            elif len(parts) == 1:
                key = parts[0]
                self._sshd_config[key] = None


    def get_config(self) -> dict:
        return self._sshd_config


    def get_config_section(self, key: str) -> str|set:
        return self._sshd_config.get(str.casefold(key))
