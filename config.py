import os
from pathlib import Path
from typing import Optional

from environs import Env
from marshmallow.validate import OneOf, Range, Regexp

HERE: Path = Path(__file__).resolve().parent

env = Env()
env.read_env()

color_re = r"(?:(?:[A-Fa-f0-9]{3}){1,2})"
_img_cache = str(HERE / ".cache" / "images")


BASE_PATH = HERE
DEBUG: bool = env.bool("DEBUG", default=False)
REDIS_URL: Optional[str] = env("REDIS_URL", default=None)
LOG_DIR: Optional[str] = env("LOG_DIR", default=None)
LOG_FILE_NAME: Optional[str] = env("LOG_FILE_NAME", default=None)
LOG_LEVEL: int = env.log_level("LOG_LEVEL", default="INFO")
MAX_AGE: int = env.int("MAX_AGE", default=86400)

HSTS_SECONDS: int = env.int("HSTS_SECONDS", default=0, validate=[Range(0)])
HSTS_INCLUDE_SUBDOMAINS: bool = env.bool("HSTS_INCLUDE_SUBDOMAINS", default=False)
HSTS_PRELOAD: bool = env.bool("HSTS_PRELOAD", default=False)

SEND_FILE_MAX_AGE_DEFAULT: int = env.int(
    "SEND_FILE_MAX_AGE_DEFAULT", default=86400, validate=[Range(0)]
)

SAVED_IMAGES_MAX_SIZE: int = env.int(
    "SAVED_IMAGES_MAX_SIZE", default=int(128e6), validate=[Range(1)]
)
SAVED_IMAGES_CACHE_DIR: Path = env.path("SAVED_IMAGES_CACHE_DIR", default=_img_cache)

SESSION_COOKIE_SECURE: bool = env.bool("SESSION_COOKIE_SECURE", default=False)
SESSION_COOKIE_SAMESITE: Optional[bool] = env.bool(
    "SESSION_COOKIE_SAMESITE", default=None
)

INDEX_DEFAULT_WIDTH: int = env.int(
    "INDEX_DEFAULT_WIDTH", default=638, validate=[Range(1)]
)
INDEX_DEFAULT_HEIGHT: int = env.int(
    "INDEX_DEFAULT_HEIGHT", default=328, validate=[Range(1)]
)
INDEX_DEFAULT_BG: str = env(
    "INDEX_DEFAULT_BG", default="cef", validate=[Regexp(color_re)]
)
INDEX_DEFAULT_FG: str = env(
    "INDEX_DEFAULT_FG", default="555", validate=[Regexp(color_re)]
)
INDEX_TEXT: str = env("INDEX_TEXT", default="Something Funny")
INDEX_DEFAULT_FORMAT: str = env(
    "INDEX_DEFAULT_FORMAT",
    default="png",
    validate=[OneOf(["png", "webp", "jpeg", "gif"])],
)
INDEX_IMG_MAX_WIDTH: int = env.int(
    "INDEX_IMG_MAX_WIDTH", default=8192, validate=[Range(1)]
)
INDEX_IMG_MAX_HEIGHT: int = env.int(
    "INDEX_IMG_MAX_HEIGHT", default=4608, validate=[Range(1)]
)

HASH_IMG_FILE_NAMES: bool = env.bool("HASH_IMG_FILE_NAMES", default=not DEBUG)


def rel_to_root(p: os.PathLike) -> str:
    return os.path.relpath(p, BASE_PATH)
