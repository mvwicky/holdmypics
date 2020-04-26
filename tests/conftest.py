from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from _pytest.tmpdir import TempPathFactory


@pytest.fixture(scope="session", name="config")
def config_fixture(tmp_path_factory: "TempPathFactory"):
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
