import pytest


def pytest_addoption(parser):
    group = parser.getgroup("holdmypics")
    group.addoption(
        "--formats",
        nargs="+",
        choices=["webp", "png", "jpeg", "gif"],
        default=["webp", "png", "jpeg"],
        help="The image formats to test.",
    )
    group.addoption(
        "--widths",
        nargs="+",
        type=int,
        default=[100, 1000],
        help="The width values to create.",
    )
    group.addoption(
        "--heights",
        nargs="+",
        type=int,
        default=[100, 1000],
        help="The height values to create.",
    )
    group.addoption(
        "--dpis", nargs="+", default=[72], type=int, help="The dpi values to use.",
    )
    group.addoption("--no-empty-dpi", action="store_false", dest="empty_dpi")


def pytest_generate_tests(metafunc):
    config = metafunc.config
    fixtures = metafunc.fixturenames
    if "image_format" in fixtures:
        formats = config.getoption("formats")
        metafunc.parametrize("image_format", formats)
    if "height" in fixtures:
        heights = config.getoption("heights")
        metafunc.parametrize("height", heights)
    if "width" in fixtures:
        widths = config.getoption("widths")
        metafunc.parametrize("width", widths)
    if "dpi" in fixtures:
        dpis = config.getoption("dpis")
        if config.getoption("empty_dpi") and None not in dpis:
            dpis.append(None)
        metafunc.parametrize("dpi", dpis)


@pytest.fixture(scope="session", name="config")
def config_fixture(tmp_path_factory):
    from config import Config

    image_dir = tmp_path_factory.mktemp("holdmypics-images")

    class TestConfig(Config):
        DEBUG = False
        TESTING = True
        SAVED_IMAGES_MAX_NUM = 250
        LOG_FILE_NAME = "holdmypics-test"
        SAVED_IMAGES_CACHE_DIR = image_dir

    return TestConfig


@pytest.fixture()
def app(config):
    from holdmypics import create_app

    app = create_app(config_class=config)

    return app


@pytest.fixture()
def client(app):
    with app.test_client() as client:
        yield client
