from __future__ import annotations

import os
from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import partial
from types import MappingProxyType
from typing import Any, ClassVar, Generic, Literal, Optional, TypeVar, Union

from attrs import define, field
from loguru import logger
from PIL import Image

from .. import redisw
from ..utils import config_value, get_size, natsize
from .args import BaseImageArgs
from .files import files
from .utils import normalize_fmt, resolve_color

_Args = TypeVar("_Args", bound=BaseImageArgs)


get_nat = partial(natsize, fmt="{0:.1f}")


def _jpeg_opt_kw(args: BaseImageArgs) -> dict[str, Any]:
    return {
        "optimize": config_value("JPEG_OPTIMIZE", cast_as=bool),
        "quality": config_value("JPEG_QUALITY", 75),
        "dpi": (args.dpi, args.dpi),
    }


def _png_opt_kw(args: BaseImageArgs) -> dict[str, Any]:
    return {
        "optmize": config_value("PNG_OPTIMIZE", True, cast_as=bool),
        "dpi": (args.dpi, args.dpi),
        "compress_level": config_value("PNG_COMPRESS_LEVEL", 6),
    }


def _webp_opt_kw(args: BaseImageArgs) -> dict[str, Any]:
    return {
        "quality": config_value("WEBP_QUALITY"),
        "method": config_value("WEBP_METHOD"),
        "lossless": config_value("WEBP_LOSSLESS", cast_as=bool),
    }


def _gif_opt_kw(args: BaseImageArgs) -> dict[str, Any]:
    return {"optmize": config_value("GIF_OPTIMIZE", cast_as=bool)}


SAVE_KW = MappingProxyType[str, Callable[[BaseImageArgs], dict[str, Any]]](
    {
        "jpeg": _jpeg_opt_kw,
        "png": _png_opt_kw,
        "webp": _webp_opt_kw,
        "gif": _gif_opt_kw,
    }
)


def _default_kw(*args: object, **kwargs: object) -> dict[str, Any]:
    return {}


@define()
class BaseGeneratedImage(Generic[_Args], ABC):
    mode: ClassVar[Literal["RGBA"]] = "RGBA"

    size: tuple[int, int]
    fmt: str = field(converter=normalize_fmt)
    bg_color: str = field(converter=resolve_color)
    fg_color: str = field(converter=resolve_color)
    args: _Args

    def new_image(
        self,
        size: Optional[tuple[int, int]] = None,
        color: Union[float, tuple[float, float, float, float], str, None] = None,
    ) -> Image.Image:
        return Image.new(self.mode, size or self.size, color or self.bg_color)

    def get_save_kw(self) -> dict[str, Any]:
        return SAVE_KW.get(self.fmt, _default_kw)(self.args)

    @abstractmethod
    def make(self) -> Image.Image:
        ...

    def get_file_name_extra(self) -> tuple[Any, ...]:
        return ()

    def get_img_path(self) -> str:
        extra = self.get_file_name_extra()
        return files.get_file_name(
            self.size, self.bg_color, self.fg_color, self.fmt, self.args, *extra
        )

    def save_img(self, im: Image.Image, path: str) -> None:
        if self.fmt == "jpeg":
            im = im.convert("RGB")
        save_kw = self.get_save_kw()
        im.save(path, **save_kw)
        im.close()
        size = get_size(path)
        logger.info("Created {0!r} ({1})", os.path.basename(path), get_nat(size))
        redisw.incr_count()
        redisw.incr_size(size)

    def get_path(self) -> str:
        path = self.get_img_path()
        if os.path.isfile(path):
            os.utime(path)
            logger.debug("Already existed: {0!r}", os.path.basename(path))
        else:
            self.save_img(self.make(), path)
        return path
