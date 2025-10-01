import pytest
import os

class BlockDevices:
    def list_devices(self) -> list[str]:
        return os.listdir("/dev/disk/by-path")

    def contains(self, device_name: str, substring: bool=False) -> bool:
        devices = self.list_devices()
        if substring:
            return any([device_name in device for device in devices])
        else:
            return device_name in devices


@pytest.fixture
def block_devices():
    return BlockDevices()
