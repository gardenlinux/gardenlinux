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
        default="test_config.yaml",
        help="Test configuration file"
    )
#    parser.addoption(
#        "--debug",
#        action="store_true",
#        help="debug"
#    )


def pytest_generate_tests(metafunc):
    option = metafunc.config.getoption("iaas")
    if "iaas" in metafunc.fixturenames:
        metafunc.parametrize("iaas", [option], scope="module")
    configfile = metafunc.config.getoption("configfile")
    if "configFile" in metafunc.fixturenames:
        metafunc.parametrize("configFile", [configfile], scope="module")
