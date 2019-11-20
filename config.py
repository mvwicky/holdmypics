import logging
from pathlib import Path

from environs import Env

HERE: Path = Path(__file__).resolve().parent
logger = logging.getLogger(__name__)

env = Env()
env.read_env()

_img_cache = str(HERE / ".cache" / "images")


class BaseConfig(object):
    DEBUG = env.bool("DEBUG", default=False)
    REDIS_URL = env("REDIS_URL")


class Config(BaseConfig):
    MAX_AGE = env.int("MAX_AGE", default=86400)
    SEND_FILE_MAX_AGE_DEFAULT = env.int("SEND_FILE_MAX_AGE_DEFAULT", default=86400)
    IMAGE_CACHE_SIZE = env.int(
        "IMAGE_CACHE_SIZE", default=128, validate=lambda s: s >= 0
    )
    with env.prefixed("SAVED_IMAGES_"):
        SAVED_IMAGES_MAX_NUM = env.int("MAX_NUM", default=50)
        SAVED_IMAGES_MAX_SIZE = env.int("MAX_SIZE", default=1024)
        SAVED_IMAGES_CACHE_DIR = env.path("CACHE_DIR", default=_img_cache)
