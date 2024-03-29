from __future__ import annotations

import os
from pathlib import Path

from environs import Env
from marshmallow.validate import OneOf, Range, Regexp

HERE: Path = Path(__file__).resolve().parent

env = Env()
env.read_env()

color_re = r"(?:(?:[A-Fa-f0-9]{3}){1,2})"
_img_cache = str(HERE / ".cache" / "images")


BASE_PATH = HERE
DEBUG: bool = env.bool("DEBUG", default=False)
REDIS_URL: str | None = env("REDIS_URL", default=None)
LOG_DIR: str | None = env("LOG_DIR", default=None)
LOG_FILE_NAME: str | None = env("LOG_FILE_NAME", default=None)
LOG_LEVEL: int = env.log_level("LOG_LEVEL", default="INFO")
MAX_LOG_SIZE: int = env.int("MAX_LOG_SIZE", default=524288)
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
SESSION_COOKIE_SAMESITE: bool | None = env.bool("SESSION_COOKIE_SAMESITE", default=None)

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

TILED_DEFAULT_WIDTH: int = env.int(
    "TILED_DEFAULT_WIDTH", default=INDEX_DEFAULT_WIDTH, validate=[Range(1)]
)
TILED_DEFAULT_HEIGHT: int = env.int(
    "TILED_DEFAULT_HEIGHT", default=INDEX_DEFAULT_HEIGHT, validate=[Range(1)]
)
TILED_DEFAULT_COLUMNS: int = env.int(
    "TILED_DEFAULT_COLUMNS", default=10, validate=[Range(1)]
)
TILED_DEFAULT_ROWS: int = env.int("TILED_DEFAULT_ROWS", default=8, validate=[Range(1)])
TILED_DEFAULT_FORMAT: str = env(
    "TILED_DEFAULT_FORMAT",
    default=INDEX_DEFAULT_FORMAT,
    validate=[OneOf(["png", "webp", "jpeg", "gif"])],
)
TILED_IMG_MAX_WIDTH: int = env.int(
    "TILED_IMG_MAX_WIDTH", default=INDEX_IMG_MAX_WIDTH, validate=[Range(1)]
)
TILED_IMG_MAX_HEIGHT: int = env.int(
    "TILED_IMG_MAX_HEIGHT", default=INDEX_IMG_MAX_HEIGHT, validate=[Range(1)]
)

HASH_IMG_FILE_NAMES: bool = env.bool("HASH_IMG_FILE_NAMES", default=not DEBUG)

JPEG_OPTIMIZE: bool = env.bool("JPEG_OPTIMIZE", default=True)
JPEG_QUALITY: int = env.int("JPEG_QUALITY", default=75, validate=[Range(0, 95)])

PNG_OPTIMIZE: bool = env.bool("PNG_OPTIMIZE", default=True)
PNG_COMPRESS_LEVEL: int = env.int(
    "PNG_COMPRESS_LEVEL", default=6, validate=[Range(0, 9)]
)

WEBP_QUALITY: int = env.int("WEBP_QUALITY", default=100, validate=[Range(0, 100)])
WEBP_METHOD: int = env.int("WEBP_METHOD", default=6, validate=[Range(0, 6)])
WEBP_LOSSLESS: bool = env.bool("WEBP_LOSSLESS", default=False)

GIF_OPTIMIZE: bool = env.bool("GIT_OPTIMIZE", default=True)


def rel_to_root(p: os.PathLike) -> str:
    return os.path.relpath(p, BASE_PATH)
