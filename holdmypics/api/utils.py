from __future__ import annotations

import functools
import random
from string import hexdigits
from typing import NamedTuple

from loguru import logger
from PIL import Image, ImageDraw
from PIL.ImageFont import ImageFont

from ..constants import PX_PER_PT
from ..fonts import fonts
from ..utils import profile


class FontParams(NamedTuple):
    font: ImageFont
    size: tuple[int, int]


class TextArgs(NamedTuple):
    color: str
    text: str
    font_name: str
    debug: bool


RAND_COLOR = "rand".casefold()
MAX_TEXT_HEIGHT = 0.9


@functools.lru_cache(maxsize=8)
def normalize_fmt(fmt: str) -> str:
    return "jpeg" if fmt == "jpg" else fmt


def random_color() -> str:
    """Generate a random hex string."""
    return "".join("{0:02x}".format(random.randrange(1 << 8)) for _ in range(3))


def px_to_pt(px: float) -> float:
    """Convert pixels to points."""
    return px * PX_PER_PT


def pt_to_px(pt: float) -> float:
    """Convert points to pixels."""
    return pt / PX_PER_PT


def guess_font_size(height: int, font_name: str) -> tuple[ImageFont, int]:
    """Try and figure out the correct font size for a given height and font.

    Args:
        ``height``: The height of the image in pixels.
        ``font_name``: The name of the font we're using.

    Returns:
        A size and an index.
    """
    font = fonts[font_name]
    # Don't want text to take up 100% of the height.
    height_prime = height * MAX_TEXT_HEIGHT
    # The image height in points.
    pt_size = int(px_to_pt(int(height_prime)))
    if pt_size in font:
        # If this point value is an actual font size, return it.
        idx = fonts.font_sizes.index(pt_size)
        logger.debug("Returning {0} with size {1} ({2})", font_name, pt_size, idx)
        return font[pt_size], idx
    s_mod = pt_size - (pt_size % 4)
    if s_mod in font:
        idx = fonts.font_sizes.index(s_mod)
        logger.debug("Returning {0} with size {1} ({2})", font_name, s_mod, idx)
        return font[s_mod], idx
    if pt_size > fonts.max_size:
        logger.debug(
            "Returning {0} with size {1} ({2})",
            font_name,
            fonts.max_size,
            len(fonts.font_sizes) - 1,
        )
        return font[fonts.max_size], len(fonts.font_sizes) - 1
    elif pt_size < fonts.min_size:
        logger.debug("Returning {0} with size {1} (0)", font_name, fonts.min_size)
        return font[fonts.min_size], 0
    last = fonts.font_sizes[0]
    for i, sz in enumerate(fonts.font_sizes[1:]):
        if last < pt_size < sz:
            logger.debug("Returning {0} with size {1} ({2})", font_name, sz, i)
            return font[sz], i
    logger.debug("Returning {0} with size {1} ({2})", font_name, sz, i)
    return font[sz], i


def get_font(d: ImageDraw.Draw, sz: tuple[int, int], args: TextArgs) -> FontParams:
    """Get the correctly sized font for the given image size and text.

    Args:
        d: An ImageDraw instance
        sz: The height and width of the output image
        args: The text parameters
    """
    font, idx = guess_font_size(sz[1], args.font_name)
    tsize = d.textsize(args.text, font)
    face = fonts[args.font_name]
    while tsize >= sz and idx > 0:  # Make the text as small as possible
        idx -= 1
        font_size = fonts.font_sizes[idx]
        font = face[font_size]
        tsize = d.textsize(args.text, font)
    logger.debug("Ended up with size {0}", fonts.font_sizes[idx])
    return FontParams(font, tsize)


@profile
def draw_text(im: Image.Image, args: TextArgs) -> Image.Image:
    w, h = im.size
    d = ImageDraw.Draw(im)
    font, tsize = get_font(d, (int(w * 0.9), h), args)
    logger.info('Writing text "{0}" (size={1})', args.text, tsize)
    tw, th = tsize
    xc, yc = int((w - tw) / 2), int((h - th) / 2)
    d.text((xc, yc), args.text, font=font, fill=args.color, align="center")
    if args.debug:
        d.rectangle(
            [(xc, yc), (int((w + tw) / 2), int((h + th) / 2))], outline="#000", width=3
        )
    return im


@functools.lru_cache(maxsize=128)
def get_color(color: str) -> str:
    color = color.lstrip("#").casefold()
    if not all(e in hexdigits for e in color):
        logger.warning("Unable to create hex color from `{0}`", color)
        return color
    n = len(color)
    if n in (3, 4):
        color = "".join(c * 2 for c in color)
    if len(color) == 6:
        color = "".join((color, "ff"))
    if len(color) in {3, 4, 6, 8}:
        return "".join(["#", color])
    logger.warning("Unable to create hex color from {0}", color)
    return color


def resolve_color(col: str) -> str:
    col = col.casefold()
    col = col if col != RAND_COLOR else random_color()
    return get_color(col)
