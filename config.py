from pathlib import Path

from environs import Env
from marshmallow.validate import Range, Regexp

HERE: Path = Path(__file__).resolve().parent

env = Env()
env.read_env()

color_re = r"(?:(?:[A-Fa-f0-9]{3}){1,2})"
_img_cache = str(HERE / ".cache" / "images")


class Config(object):
    BASE_PATH = HERE
    DEBUG = env.bool("DEBUG", default=False)
    REDIS_URL = env("REDIS_URL", default=None)
    LOG_DIR = env("LOG_DIR", default=None)
    LOG_FILE_NAME = env("LOG_FILE_NAME", default=None)
    LOG_LEVEL = env.log_level("LOG_LEVEL", default="INFO")
    MAX_AGE = env.int("MAX_AGE", default=86400)

    HSTS_SECONDS = env.int("HSTS_SECONDS", default=0)
    HSTS_INCLUDE_SUBDOMAINS = env.bool("HSTS_INCLUDE_SUBDOMAINS", default=False)
    HSTS_PRELOAD = env.bool("HSTS_PRELOAD", default=False)

    SEND_FILE_MAX_AGE_DEFAULT = env.int("SEND_FILE_MAX_AGE_DEFAULT", default=86400)
    IMAGE_CACHE_SIZE = env.int(
        "IMAGE_CACHE_SIZE", default=128, validate=[Range(min=0, min_inclusive=True)]
    )

    SAVED_IMAGES_MAX_NUM = env.int("SAVED_IMAGES_MAX_NUM", default=50)
    SAVED_IMAGES_MAX_SIZE = env.int("SAVED_IMAGES_MAX_SIZE", default=1024)
    SAVED_IMAGES_CACHE_DIR = env.path("SAVED_IMAGES_CACHE_DIR", default=_img_cache)

    SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=False)
    SESSION_COOKIE_SAMESITE = env.bool("SESSION_COOKIE_SAMESITE", default=None)

    INDEX_DEFAULT_BG = env(
        "INDEX_DEFAULT_BG", default="cef", validate=[Regexp(color_re)]
    )
    INDEX_DEFAULT_FG = env(
        "INDEX_DEFAULT_FG", default="eee", validate=[Regexp(color_re)]
    )
    INDEX_TEXT = env("INDEX_TEXT", default="Something Funny")
