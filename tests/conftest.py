import os
from typing import TYPE_CHECKING

import pytest
from environs import Env
from hypothesis import settings
from loguru import logger
from marshmallow.validate import OneOf

if TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.tmpdir import TempPathFactory

PROFILES = {
    "ci": {"max_examples": 50, "deadline": None},
    "dev": {"max_examples": 25, "deadline": None},
}


def _log_filt(record: dict) -> bool:
    return "test" in record["name"]


def pytest_configure(config: "Config"):
    env = Env()
    env.read_env()
    fmt = (
        "[<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>] | "
        "<level>{level:<8}</level> | "
        "<blue>{name}</blue>:<cyan>{line}</cyan> - <bold>{message}</bold>"
    )
    log_file = os.path.join("log", "holdmytests.log")
    logger.add(log_file, format=fmt, level="DEBUG", filter=_log_filt)
    for name, kwargs in PROFILES.items():
        settings.register_profile(name, **kwargs)
    profile = env("HYPOTHESIS_PROFILE", default="ci", validate=OneOf(list(PROFILES)))
    settings.load_profile(profile)


@pytest.fixture(scope="session", name="config")
def config_fixture(tmp_path_factory: "TempPathFactory"):
    from config import Config

    image_dir = tmp_path_factory.mktemp("holdmypics-images")
    logger.info("Image dir: {0}", image_dir)

    class TestConfig(Config):
        DEBUG = False
        TESTING = True
        SAVED_IMAGES_MAX_NUM = 250
        LOG_FILE_NAME = "holdmypics-test"
        # SAVED_IMAGES_CACHE_DIR = image_dir

    return TestConfig


@pytest.fixture()
def app(config):
    from holdmypics import create_app

    app = create_app(config)

    return app


@pytest.fixture()
def client(app):
    with app.test_client() as client:
        yield client
