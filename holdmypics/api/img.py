from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any, ClassVar

import attr
from loguru import logger
from PIL import Image

from .. import redisw
from ..constants import COUNT_KEY, RAND_COLOR
from ..utils import natsize
from .args import ImageArgs
from .files import files, get_size
from .utils import TextArgs, draw_text, get_color, normalize_fmt, random_color

OPT_KW: dict[str, Callable[[ImageArgs], dict[str, Any]]] = {
    "jpeg": lambda args: {"optimize": True, "dpi": (args.dpi, args.dpi)},
    "png": lambda args: {"optimize": True, "dpi": (args.dpi, args.dpi)},
    "webp": lambda _: {"quality": 100, "method": 6},
    "gif": lambda _: {"optimize": True},
}


def color_converter(col: str) -> str:
    col = str.casefold(col)
    col = col if col != RAND_COLOR else random_color()
    return get_color(col)


@attr.s(slots=True, auto_attribs=True)
class GeneratedImage(object):
    mode: ClassVar[str] = "RGBA"

    size: tuple[int, int]
    bg_color: str = attr.ib(converter=color_converter)
    fg_color: str = attr.ib(converter=color_converter)
    fmt: str = attr.ib(converter=normalize_fmt)
    args: ImageArgs

    def get_save_kw(self) -> dict[str, Any]:
        kw_func = OPT_KW.get(self.fmt, None)
        if kw_func is not None:
            return kw_func(self.args)
        else:
            return {}

    def make(self) -> Image.Image:
        im = Image.new(self.mode, self.size, self.bg_color)
        args = self.args
        if args.alpha < 1:
            alpha_im = Image.new("L", self.size, int(args.alpha * 255))
            im.putalpha(alpha_im)
        if args.text is not None:
            text_args = TextArgs(self.fg_color, args.text, args.font_name, args.debug)
            im = draw_text(im, text_args)
        if self.fmt == "jpeg":
            im = im.convert("RGB")
        return im

    def get_path(self) -> str:
        path = files.get_file_name(
            self.size, self.bg_color, self.fg_color, self.fmt, self.args
        )
        if os.path.isfile(path):
            os.utime(path)
            logger.debug('Already existed: "{0}"', os.path.basename(path))
            return path
        else:
            im = self.make()
            save_kw = self.get_save_kw()
            im.save(path, **save_kw)
            im.close()
            sz = natsize(get_size(path), fmt="{0:.1f}")
            logger.info('Created "{0}" ({1})', os.path.basename(path), sz)
            redisw.client.incr(COUNT_KEY)
        return path
