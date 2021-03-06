import os
from typing import Callable, Dict, Tuple, Union

from humanize import naturalsize
from loguru import logger
from PIL import Image

from .. import redisw
from .._types import Dimension
from ..constants import COUNT_KEY
from ..converters import RAND_COLOR
from ..utils import profile
from .args import ImageArgs
from .files import files
from .utils import TextArgs, draw_text, get_color, normalize_fmt, random_color

OptValues = Union[str, bool, int, Tuple[int, int]]

MODE = "RGBA"

opt_kw: Dict[str, Callable[[ImageArgs], Dict[str, OptValues]]] = {
    "jpeg": lambda args: {"optimize": True, "dpi": (args.dpi, args.dpi)},
    "png": lambda args: {"optimize": True, "dpi": (args.dpi, args.dpi)},
    "webp": lambda _: {"quality": 100, "method": 6},
    "gif": lambda _: {"optimize": True},
}


@profile
def make_image(
    size: Dimension, bg_color: str, fg_color: str, fmt: str, args: ImageArgs
) -> Image.Image:
    fmt = normalize_fmt(fmt)
    im = Image.new(MODE, size, bg_color)
    if args.alpha < 1:
        alpha_im = Image.new("L", size, int(args.alpha * 255))
        im.putalpha(alpha_im)
    if args.text is not None:
        text_args = TextArgs(fg_color, args.text, args.font_name, args.debug)
        im = draw_text(im, text_args)
    if fmt == "jpeg":
        im = im.convert("RGB")
    return im


def save_image(
    size: Dimension, bg_color: str, fg_color: str, fmt: str, args: ImageArgs
) -> str:
    """Create an image or find an existing one and produce its path."""
    fmt = normalize_fmt(fmt)
    bg_color, fg_color = map(str.casefold, (bg_color, fg_color))
    if bg_color == RAND_COLOR:
        bg_color = random_color()
    if fg_color == RAND_COLOR:
        fg_color = random_color()

    bg_color, fg_color = get_color(bg_color), get_color(fg_color)
    path = files.get_file_name(size, bg_color, fg_color, fmt, args)

    if os.path.isfile(path):
        os.utime(path)
        logger.debug("Already existed")
        return path
    else:
        im = make_image(size, bg_color, fg_color, fmt, args)
        save_kw = {}
        kw_func = opt_kw.get(fmt, None)
        if kw_func is not None:  # pragma: no cover
            save_kw.update(kw_func(args))
        im.save(path, **save_kw)
        im.close()
        sz = naturalsize(os.path.getsize(path), format="%.3f")
        logger.info('Created "{0}" ({1})', path, sz)
        redisw.client.incr(COUNT_KEY)
        return path
