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

MAX_LOG_SIZE = 3 * (1024 ** 2)
PROFILES = {
    "ci": {"max_examples": 50, "deadline": None},
    "dev": {"max_examples": 25, "deadline": None},
}


def configure_logging():
    fmt = (
        "[<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>] <level>{level:<8}</level> "
        "<blue>{name}</blue>:<cyan>{line}</cyan> - <bold>{message}</bold>"
    )
    log_file = os.path.join("log", "holdmytests.log")
    log_kw = {
        "format": fmt,
        "level": "DEBUG",
        "compression": "tar.gz",
        "retention": 5,
        "rotation": MAX_LOG_SIZE,
    }
    logger.add(log_file, **log_kw)


def pytest_configure(config: "Config"):
    env = Env()
    env.read_env()
    configure_logging()

    for name, kwargs in PROFILES.items():  # type: str, dict
        settings.register_profile(name, **kwargs)

    pr_validate = [OneOf(list(PROFILES))]
    profile = env("HYPOTHESIS_PROFILE", default="ci", validate=pr_validate)
    settings.load_profile(profile)


@pytest.fixture(scope="session", name="config")
def config_fixture(tmp_path_factory: "TempPathFactory"):
    import config as _config

    image_dir = tmp_path_factory.mktemp("holdmypics-images")
    logger.info("Image dir: {0}", image_dir)
    test_config = {
        "DEBUG": False,
        "TESTING": True,
        "SAVED_IMAGES_MAX_NUM": 250,
        "LOG_FILE_NAME": "holdmypics-test",
        "SAVED_IMAGES_CACHE_DIR": image_dir,
    }
    _config.__dict__.update(test_config)

    return _config


@pytest.fixture()
def app(config):
    from holdmypics import create_app

    app = create_app(config)

    return app


@pytest.fixture()
def client(app):
    with app.test_client() as client:
        yield client
