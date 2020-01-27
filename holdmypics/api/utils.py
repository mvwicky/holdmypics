import os
import random
from string import hexdigits

import attr
from PIL import Image, ImageDraw

from .. import redis_client
from .._types import Dimension
from ..constants import COUNT_KEY, MAX_SIZE, MIN_SIZE, font_sizes, fonts
from .files import files
from .image_args import ImageArgs


def random_color():
    return "".join([f"{random.randrange(256):02x}" for _ in range(3)])


def px_to_pt(px: float) -> float:
    """Convert pixels to points."""
    return px * 0.75


def pt_to_px(pt: float) -> float:
    return pt / 0.75


def guess_size(height: int, font_name: str):
    """Try and figure out the correct font size for a given height and font.

    Arguments:
        height: The height of the image in pixels
        font_name: The name of the font we're using.

    Returns:
        A size and an index.
    """
    font = fonts[font_name]
    # Don't want text to take up 100% of the height.
    height_prime = height * 0.75
    # The image height in points.
    pt_size = int(px_to_pt(int(height_prime)))
    if pt_size in font:
        # If this point value is an actual font size, return it.
        return font[pt_size], font_sizes.index(pt_size)
    s_mod = pt_size - (pt_size % 4)
    if s_mod in font:
        return font[s_mod], font_sizes.index(s_mod)
    if pt_size > MAX_SIZE:
        return font[MAX_SIZE], len(font_sizes) - 1
    elif pt_size < MIN_SIZE:
        return font[MIN_SIZE], 0
    last = font_sizes[0]
    for i, sz in enumerate(font_sizes[1:]):
        if last < pt_size < sz:
            return font[sz], i


def get_font(d: ImageDraw.Draw, sz: Dimension, text: str, font_name: str):
    face = fonts[font_name]
    width, height = sz
    font, idx = guess_size(height, font_name)
    tsize = d.textsize(text, font)
    while tsize >= sz and idx > 0:
        idx -= 1
        font = face[font_sizes[idx]]
        tsize = d.textsize(text, font)
    return font, tsize


def draw_text(im: Image.Image, color: str, args: ImageArgs):
    w, h = im.size
    txt = Image.new("RGBA", im.size, (255, 255, 255, 0))
    d = ImageDraw.Draw(txt)
    font, tsize = get_font(d, (int(w * 0.9), h), args.text, args.font_name)
    tw, th = tsize
    xc = int((w - tw) / 2)
    yc = int((h - th) / 2)
    d.text((xc, yc), args.text, font=font, fill=color, align="center")
    if args.debug:
        d.rectangle(
            [(xc, yc), (int((w + tw) / 2), int((h + th) / 2))], outline="#000", width=3
        )

    return Image.alpha_composite(im, txt)


fmt_kw = {
    "jpeg": lambda args: {"optimize": True, "dpi": (args.dpi, args.dpi)},
    "png": lambda args: {"optimize": True, "dpi": (args.dpi, args.dpi)},
    "webp": lambda _: {"quality": 100, "method": 6},
    "gif": lambda _: {"optimize": True},
}


def make_image(
    size: Dimension, bg_color: str, fg_color: str, fmt: str, args: ImageArgs
):
    fmt = "jpeg" if fmt == "jpg" else fmt
    mode = "RGBA"
    bg_color = get_color(bg_color)
    fg_color = get_color(fg_color)
    path = files.get_file_name(size, bg_color, fg_color, fmt, *attr.astuple(args))

    if os.path.isfile(path):
        return path
    else:
        redis_client.incr(COUNT_KEY)
        save_kw = {}
        kw_func = fmt_kw.get(fmt, None)
        if kw_func is not None:
            save_kw.update(kw_func(args))

        im = Image.new(mode, size, bg_color)
        if args.alpha < 1:
            alpha_im = Image.new("L", size, int(args.alpha * 255))
            im.putalpha(alpha_im)
        if args.text is not None and fmt != "jpeg":
            im = draw_text(im, fg_color, args)
        if fmt == "jpeg":
            im = im.convert("RGB")
        im.save(path, **save_kw)
        return path


def get_color(color: str) -> str:
    color = color.lstrip("#")
    color_len = len(color)
    if color_len in {3, 6} and all(e in hexdigits for e in color):
        return "#" + color
    return color
