import os

import attr
from PIL import Image

from .. import redisw
from .._types import Dimension
from ..constants import COUNT_KEY
from .files import files
from .args import ImageArgs
from .utils import draw_text, fmt_kw, get_color


def make_image(
    size: Dimension, bg_color: str, fg_color: str, fmt: str, args: ImageArgs
) -> str:
    fmt = "jpeg" if fmt == "jpg" else fmt
    mode = "RGBA"
    bg_color = get_color(bg_color)
    fg_color = get_color(fg_color)
    path = files.get_file_name(size, bg_color, fg_color, fmt, *attr.astuple(args))

    if os.path.isfile(path):
        os.utime(path)
        return path
    else:
        im = Image.new(mode, size, bg_color)
        if args.alpha < 1:
            alpha_im = Image.new("L", size, int(args.alpha * 255))
            im.putalpha(alpha_im)
        if args.text is not None and fmt != "jpeg":
            im = draw_text(im, fg_color, args)
        if fmt == "jpeg":
            im = im.convert("RGB")
        save_kw = {}
        kw_func = fmt_kw.get(fmt, None)
        if kw_func is not None:
            save_kw.update(kw_func(args))
        im.save(path, **save_kw)
        redisw.client.incr(COUNT_KEY)
        return path
