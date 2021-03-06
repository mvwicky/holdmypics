import random
from string import hexdigits
from typing import NamedTuple, Tuple

from cytoolz import memoize
from loguru import logger
from PIL import Image, ImageDraw
from PIL.ImageFont import ImageFont

from .._types import Dimension
from ..constants import PX_PER_PT
from ..fonts import fonts
from ..utils import profile


class FontParams(NamedTuple):
    font: ImageFont
    size: Dimension


class TextArgs(NamedTuple):
    color: str
    text: str
    font_name: str
    debug: bool


font_sizes = fonts.font_sizes

RAND_COLOR = "rand".casefold()
MAX_TEXT_HEIGHT = 0.9


@memoize
def normalize_fmt(fmt: str) -> str:
    return "jpeg" if fmt == "jpg" else fmt


def random_color() -> str:
    """Generate a random hex string."""
    return "".join(["{0:02x}".format(random.randrange(1 << 8)) for _ in range(3)])


def px_to_pt(px: float) -> float:
    """Convert pixels to points."""
    return px * PX_PER_PT


def pt_to_px(pt: float) -> float:
    """Convert points to pixels."""
    return pt / PX_PER_PT


def guess_size(height: int, font_name: str) -> Tuple[ImageFont, int]:
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
        return font[pt_size], font_sizes.index(pt_size)
    s_mod = pt_size - (pt_size % 4)
    if s_mod in font:
        return font[s_mod], font_sizes.index(s_mod)
    if pt_size > fonts.max_size:
        return font[fonts.max_size], len(font_sizes) - 1
    elif pt_size < fonts.min_size:
        return font[fonts.min_size], 0
    last = font_sizes[0]
    for i, sz in enumerate(font_sizes[1:]):
        if last < pt_size < sz:
            return font[sz], i
    return font[sz], i


def get_font(d: ImageDraw.Draw, sz: Dimension, text: str, font_name: str) -> FontParams:
    """Get the correctly sized font for the given image size and text.

    Args:
        d: An ImageDraw instance
        sz: The height and width of the output image
        text: The text to be written
        font_name: The typeface that we're using.
    """
    face = fonts[font_name]
    width, height = sz
    font, idx = guess_size(height, font_name)
    tsize = d.textsize(text, font)
    while tsize >= sz and idx > 0:
        idx -= 1
        font = face[font_sizes[idx]]
        tsize = d.textsize(text, font)
    return FontParams(font, tsize)


@profile
def draw_text(im: Image.Image, args: TextArgs) -> Image.Image:
    w, h = im.size
    d = ImageDraw.Draw(im)
    font, tsize = get_font(d, (int(w * 0.9), h), args.text, args.font_name)
    logger.info(f'Writing text "{args.text}" (size={tsize})')
    tw, th = tsize
    xc = int((w - tw) / 2)
    yc = int((h - th) / 2)
    d.text((xc, yc), args.text, font=font, fill=args.color, align="center")
    if args.debug:
        d.rectangle(
            [(xc, yc), (int((w + tw) / 2), int((h + th) / 2))], outline="#000", width=3
        )
    return im


@memoize
def get_color(color: str) -> str:
    color = color.lstrip("#").casefold()
    if len(color) in {3, 6} and all(e in hexdigits for e in color):
        return "".join(["#", color])
    return color
