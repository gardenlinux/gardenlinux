import pytest
from _pytest.config.argparsing import Parser


def pytest_addoption(parser: Parser):
    parser.addoption(
        "--severity",
        action="store",
        default="warning",
        help="Severity level of shellcheck (error, warning, info, style)",
    )


@pytest.fixture
def severity_level(request):
    return request.config.getoption("--severity")
