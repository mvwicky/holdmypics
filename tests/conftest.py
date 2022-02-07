from __future__ import annotations

import os
from collections.abc import Callable, Iterable
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from environs import Env
from hypothesis import HealthCheck, settings
from loguru import logger
from marshmallow.validate import OneOf

if TYPE_CHECKING:
    from types import ModuleType

    from flask.testing import FlaskClient

    from holdmypics import Holdmypics

MAX_LOG_SIZE = 3 * (1024**2)
COMMON_PROFILE = {
    "suppress_health_check": (HealthCheck.data_too_large,),
    "deadline": None,
}
PROFILES = {
    "ci": {"max_examples": 50, **COMMON_PROFILE},
    "dev": {"max_examples": 15, **COMMON_PROFILE},
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


def pytest_configure(config: pytest.Config):
    env = Env()
    env.read_env()
    configure_logging()

    for name in PROFILES:
        settings.register_profile(name, **PROFILES[name])

    profile = env("HYPOTHESIS_PROFILE", default="ci", validate=[OneOf(PROFILES)])
    settings.load_profile(profile)


@pytest.fixture(scope="session", name="config")
def config_fixture(
    tmp_path_factory: pytest.TempPathFactory, pytestconfig: pytest.Config
) -> "ModuleType":
    import config as _config

    image_dir = pytestconfig.getoption("--image-dir", None)
    if image_dir is not None:
        image_dir = Path(image_dir).resolve()
    else:
        image_dir = tmp_path_factory.mktemp("holdmypics-images")
    logger.info("Image dir: {0}", image_dir)
    test_config = {
        "DEBUG": False,
        "SAVED_IMAGES_MAX_SIZE": 1024 * 10,
        "LOG_FILE_NAME": "holdmypics-test",
        "SAVED_IMAGES_CACHE_DIR": image_dir,
    }
    _config.__dict__.update(test_config)
    for key, value in test_config.items():
        assert key in _config.__dict__
        _config.__dict__[key] = value
    _config.__dict__["TESTING"] = True
    return _config


@pytest.fixture(scope="module", name="app_factory")
def app_factory_fixture(config: "ModuleType") -> Callable[[], "Holdmypics"]:
    from holdmypics import create_app

    return partial(create_app, config)


@pytest.fixture()
def app(config: "ModuleType") -> "Holdmypics":
    from holdmypics import create_app

    app = create_app(config)

    return app


@pytest.fixture()
def client(app: "Holdmypics") -> Iterable["FlaskClient"]:
    with app.test_client() as client:
        yield client
