from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any, ClassVar, Generic, TypeVar

import attr
from loguru import logger
from PIL import Image

from .. import redisw
from ..constants import COUNT_KEY
from ..utils import get_size, natsize
from .args import BaseImageArgs
from .utils import normalize_fmt, resolve_color

_A = TypeVar("_A", bound=BaseImageArgs)

OPT_KW: dict[str, Callable[[BaseImageArgs], dict[str, Any]]] = {
    "jpeg": lambda args: {"optimize": True, "dpi": (args.dpi, args.dpi)},
    "png": lambda args: {"optimize": True, "dpi": (args.dpi, args.dpi)},
    "webp": lambda _: {"quality": 100, "method": 6, "lossless": False},
    "gif": lambda _: {"optimize": True},
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
        kw_func = OPT_KW.get(self.fmt, None)
        return {} if kw_func is None else kw_func(self.args)

    def make(self) -> Image.Image:
        raise NotImplementedError("Subclass must implement.")

    def save_img(self, im: Image.Image, path: str):
        save_kw = self.get_save_kw()
        im.save(path, **save_kw)
        im.close()
        sz = natsize(get_size(path), fmt="{0:.1f}")
        logger.info('Created "{0}" ({1})', os.path.basename(path), sz)
        redisw.client.incr(COUNT_KEY)
