from _pytest.config.argparsing import Parser


def pytest_addoption(parser: Parser):
    parser.addoption(
        "--iaas",
        action="store",
        default="gcp",
        help="Infrastructure the tests should run on",
    )
    parser.addoption(
        "--configfile",
        action="store",
        default="./../test_config.yaml",
        help="Test configuration file"
    )


def pytest_generate_tests(metafunc):
    option = metafunc.config.getoption("iaas")
    if "iaas" in metafunc.fixturenames:
        metafunc.parametrize("iaas", [option], scope="module")
    configfile = metafunc.config.getoption("configfile")
    if "configfile" in metafunc.fixturenames:
        metafunc.parametrize("configfile", [configfile], scope="module")
