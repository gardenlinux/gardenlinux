from _pytest.config.argparsing import Parser


def pytest_addoption(parser: Parser):
    parser.addoption(
        "--iaas",
        action="store",
        default="gcp",
        help="Infrastructure the tests should run on",
    )
    parser.addoption(
        "--config",
        action="store",
        default="test_config.yaml",
        help="test configuration file"
    )


def pytest_generate_tests(metafunc):
    option = metafunc.config.getoption("iaas")
    if "iaas" in metafunc.fixturenames:
        metafunc.parametrize("iaas", [option], scope="module")
    
    option = metafunc.config.getoption("config")
    if "configFile" in metafunc.fixturenames:
        metafunc.parametrize("configFile", [option], scope="module")
