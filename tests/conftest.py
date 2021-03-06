import pytest


from customization import c11n
c11n.state_file = 'fixtures/test_state.yaml'


def pytest_addoption(parser):
    parser.addoption(
        "--run-slow", action="store_true", default=False, help="run slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "api: mark test as scoping the web api")
    config.addinivalue_line("markers", "slow: mark test as slow to run")
    config.addinivalue_line("markers", "wip: on-going test-driven development")


def pytest_collection_modifyitems(config, items):

    if not config.getoption("--run-slow"):
        skip_slow = pytest.mark.skip(reason="need --run-slow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
