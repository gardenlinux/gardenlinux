import pytest
from .shell import ShellRunner


class Sshd:
    def __init__(self, shell: ShellRunner):
        self._shell = shell
        result = shell("/usr/sbin/sshd -T", capture_output=True, ignore_exit_code=True)
        assert (
            result.returncode == 0
        ), f"Expected return code 0, got {result.returncode}"
        self._sshd_config_text = result.stdout
        self._sshd_config = None

    def read_config(self) -> dict:
        if self._sshd_config is not None:
            return self._sshd_config
        config = {}
        for line in self._sshd_config_text.splitlines():
            if not line.strip():
                continue
            parts = line.split(maxsplit=1)
            if len(parts) == 2:
                key, value = parts
                # If key already exists, convert to set and append
                if key in config:
                    if isinstance(config[key], set):
                        config[key].add(value)
                    else:
                        config[key] = {config[key], value}
                else:
                    # fixme: this is not ideal. what we want here is to have comma separated string values
                    # as a set to make comparing them easier because the order of entries does not matter
                    # the 3 is an arbitrary number to allow for real string values with commas
                    if value.count(",") >= 3:
                        config[key] = set(value.split(","))
                    else:
                        config[key] = value
            elif len(parts) == 1:
                key = parts[0]
                config[key] = None
        self._sshd_config = config
        return config

    def get_config_section(self, key: str) -> str|set:
        config = self.read_config()
        return config.get(str.casefold(key))
