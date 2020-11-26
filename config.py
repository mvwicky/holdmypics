import os
from pathlib import Path

from environs import Env
from marshmallow.validate import OneOf, Range, Regexp

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

    HSTS_SECONDS = env.int("HSTS_SECONDS", default=0, validate=[Range(min=0)])
    HSTS_INCLUDE_SUBDOMAINS = env.bool("HSTS_INCLUDE_SUBDOMAINS", default=False)
    HSTS_PRELOAD = env.bool("HSTS_PRELOAD", default=False)

    SEND_FILE_MAX_AGE_DEFAULT = env.int(
        "SEND_FILE_MAX_AGE_DEFAULT", default=86400, validate=[Range(min=0)]
    )

    SAVED_IMAGES_MAX_NUM = env.int(
        "SAVED_IMAGES_MAX_NUM", default=50, validate=[Range(min=0)]
    )
    SAVED_IMAGES_CACHE_DIR = env.path("SAVED_IMAGES_CACHE_DIR", default=_img_cache)

    SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=False)
    SESSION_COOKIE_SAMESITE = env.bool("SESSION_COOKIE_SAMESITE", default=None)

    INDEX_DEFAULT_BG = env(
        "INDEX_DEFAULT_BG", default="cef", validate=[Regexp(color_re)]
    )
    INDEX_DEFAULT_FG = env(
        "INDEX_DEFAULT_FG", default="555", validate=[Regexp(color_re)]
    )
    INDEX_TEXT = env("INDEX_TEXT", default="Something Funny")
    INDEX_DEFAULT_FORMAT = env(
        "INDEX_DEFAULT_FORMAT",
        default="png",
        validate=[OneOf(["png", "webp", "jpeg", "gif"])],
    )
    INDEX_IMG_MAX_WIDTH = env.int(
        "INDEX_IMG_MAX_WIDTH", default=8192, validate=[Range(min=1)]
    )
    INDEX_IMG_MAX_HEIGHT = env.int(
        "INDEX_IMG_MAX_HEIGHT", default=4608, validate=[Range(min=1)]
    )

    HASH_IMG_FILE_NAMES = env.bool("HASH_IMG_FILE_NAMES", default=not DEBUG)

    @classmethod
    def rel_to_root(cls, p: os.PathLike) -> str:
        return os.path.relpath(p, cls.BASE_PATH)
