import pytest

skip_performance_metrics = False

def pytest_addoption(parser):
	parser.addoption(
		"--skip-performance-metrics",
		action="store_true",
		help="Skip performance metric tests. Useful if running in a VM under emulation."
	)

def pytest_configure(config):
	global skip_performance_metrics
	skip_performance_metrics = config.getoption("--skip-performance-metrics")

	config.addinivalue_line("markers", "performance_metric: this test is a performance metric")

def pytest_collection_modifyitems(config, items):
	for item in items:
		if item.get_closest_marker("performance_metric") and skip_performance_metrics:
			item.add_marker(pytest.mark.skip(reason="skipping performance metric tests"))
