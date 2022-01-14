from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any, ClassVar, Generic, TypeVar

import attr
from loguru import logger
from PIL import Image

from .. import redisw
from ..constants import COUNT_KEY
from ..utils import config_value, get_size, natsize
from .args import BaseImageArgs
from .utils import normalize_fmt, resolve_color

_A = TypeVar("_A", bound=BaseImageArgs)


def _jpeg_opt_kw(args: BaseImageArgs) -> dict[str, Any]:
    return {
        "optimize": config_value("JPEG_OPTIMIZE", cast=bool),
        "quality": config_value("JPEG_QUALITY", 75),
        "dpi": (args.dpi, args.dpi),
    }


def _png_opt_kw(args: BaseImageArgs) -> dict[str, Any]:
    return {
        "optmize": config_value("PNG_OPTIMIZE", True, cast=bool),
        "dpi": (args.dpi, args.dpi),
        "compress_level": config_value("PNG_COMPRESS_LEVEL", 6),
    }


def _webp_opt_kw(args: BaseImageArgs) -> dict[str, Any]:
    return {
        "quality": config_value("WEBP_QUALITY"),
        "method": config_value("WEBP_METHOD"),
        "lossless": config_value("WEBP_LOSSLESS", cast=bool),
    }


def _gif_opt_kw(args: BaseImageArgs) -> dict[str, Any]:
    return {"optmize": config_value("GIF_OPTIMIZE", cast=bool)}


SAVE_KW: dict[str, Callable[[BaseImageArgs], dict[str, Any]]] = {
    "jpeg": _jpeg_opt_kw,
    "png": _png_opt_kw,
    "webp": _webp_opt_kw,
    "gif": _gif_opt_kw,
}


@attr.s(slots=True, auto_attribs=True)
class BaseGeneratedImage(Generic[_A]):
    mode: ClassVar[str] = "RGBA"

    size: tuple[int, int]
    fmt: str = attr.ib(converter=normalize_fmt)
    bg_color: str = attr.ib(converter=resolve_color)
    fg_color: str = attr.ib(converter=resolve_color)
    args: _A

    def get_save_kw(self) -> dict[str, Any]:
        kw_func = SAVE_KW.get(self.fmt, None)
        return {} if kw_func is None else kw_func(self.args)

    def make(self) -> Image.Image:
        raise NotImplementedError("Subclass must implement.")

    def save_img(self, im: Image.Image, path: str):
        save_kw = self.get_save_kw()
        im.save(path, **save_kw)
        logger.debug("Closing image {0}", path)
        im.close()
        sz = natsize(get_size(path), fmt="{0:.1f}")
        logger.info('Created "{0}" ({1})', os.path.basename(path), sz)
        redisw.client.incr(COUNT_KEY)
