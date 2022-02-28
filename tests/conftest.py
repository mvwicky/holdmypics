from __future__ import annotations

import os
import time
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import TYPE_CHECKING, cast

import attr
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
PROFILES = {
    "ci": {"max_examples": 50, "derandomize": True},
    "dev": {"max_examples": 15},
}


@attr.s(slots=True, auto_attribs=True, frozen=True)
class AppFactory(object):
    factory: Callable[[ModuleType], Holdmypics] = attr.ib(repr=False)
    config: ModuleType = attr.ib(repr=False)

    def __call__(self) -> Holdmypics:
        return self.factory(self.config)


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
    # configure_logging()

    deadline = env.timedelta("HYPOTHESIS_DEADLINE", default=None)
    common_settings = settings(
        suppress_health_check=(HealthCheck.data_too_large,), deadline=deadline
    )
    for name in PROFILES:
        settings.register_profile(name, common_settings, **PROFILES[name])

    profile = env("HYPOTHESIS_PROFILE", default="ci", validate=[OneOf(PROFILES)])
    settings.load_profile(profile)


@pytest.fixture(scope="session", name="config")
def config_fixture(
    tmp_path_factory: pytest.TempPathFactory, pytestconfig: pytest.Config
) -> ModuleType:
    import config as _config

    image_dir = pytestconfig.getoption("--image-dir", None)  # type: ignore
    if image_dir is not None:
        image_dir = Path(cast(str, image_dir)).resolve()
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
def app_factory_fixture(config: ModuleType) -> AppFactory:
    from holdmypics import create_app

    return AppFactory(create_app, config)


@pytest.fixture()
def app(app_factory: AppFactory) -> Holdmypics:
    return app_factory()


@pytest.fixture()
def client(app: Holdmypics) -> Iterable[FlaskClient]:
    with app.test_client() as client:
        yield client


@pytest.fixture()
def time_test(request: pytest.FixtureRequest):
    start = time.perf_counter()
    yield None
    func = cast(Callable, request.function)
    name = func.__name__
    logger.debug("Timed {0!r} - Elapsed: {1:.4f}", name, time.perf_counter() - start)
