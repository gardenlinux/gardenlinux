import pytest

from typing import Final

CLOCKSOURCE_FILE: Final[str] = "/sys/devices/system/clocksource/clocksource0/current_clocksource"
ETC_CHRONY_CONF: Final[str] = "/etc/chrony/chrony.conf"
DEV_PTP_HYPERV: Final[str] = "/dev/ptp_hyperv"

@pytest.fixture
def clocksource_file() -> str:
    return CLOCKSOURCE_FILE

@pytest.fixture
def chrony_config_file() -> str:
    return ETC_CHRONY_CONF

@pytest.fixture
def ptp_hyperv_dev() -> str:
    return DEV_PTP_HYPERV