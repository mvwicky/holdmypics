import os
from typing import Callable, Dict, Tuple, Union

import attr
from loguru import logger
from PIL import Image

from .. import redisw
from .._types import Dimension
from ..constants import COUNT_KEY
from .args import ImageArgs
from .files import files
from .utils import TextArgs, draw_text, get_color

OptValues = Union[str, bool, int, Tuple[int, int]]

opt_kw: Dict[str, Callable[[ImageArgs], Dict[str, OptValues]]] = {
    "jpeg": lambda args: {"optimize": True, "dpi": (args.dpi, args.dpi)},
    "png": lambda args: {"optimize": True, "dpi": (args.dpi, args.dpi)},
    "webp": lambda _: {"quality": 100, "method": 6},
    "gif": lambda _: {"optimize": True},
}


def make_image(
    size: Dimension, bg_color: str, fg_color: str, fmt: str, args: ImageArgs
) -> str:
    """Create an image or find an existing one and produce its path."""
    fmt = "jpeg" if fmt == "jpg" else fmt
    mode = "RGBA"
    bg_color = get_color(bg_color)
    fg_color = get_color(fg_color)
    path = files.get_file_name(size, bg_color, fg_color, fmt, *attr.astuple(args))

    if os.path.isfile(path):
        os.utime(path)
        logger.info("Already existed")
        return path
    else:
        logger.info("Creating new file")
        im = Image.new(mode, size, bg_color)
        if args.alpha < 1:
            alpha_im = Image.new("L", size, int(args.alpha * 255))
            im.putalpha(alpha_im)
        if args.text is not None:
            logger.info('Writing text "{0}"', args.text)
            text_args = TextArgs(fg_color, args.text, args.font_name, args.debug)
            im = draw_text(im, text_args)
        if fmt == "jpeg":
            im = im.convert("RGB")
        save_kw = {}
        kw_func = opt_kw.get(fmt, None)
        if kw_func is not None:
            save_kw.update(kw_func(args))
        im.save(path, **save_kw)
        redisw.client.incr(COUNT_KEY)
        return path
