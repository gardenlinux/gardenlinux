from _pytest.config.argparsing import Parser


def pytest_addoption(parser: Parser):
    parser.addoption(
        "--iaas",
        action="store",
        default="gcp",
        help="Infrastructure the tests should run on",
    )


def pytest_generate_tests(metafunc):
    option = metafunc.config.getoption("iaas")
    if "iaas" in metafunc.fixturenames:
        metafunc.parametrize("iaas", [option], scope="module")
