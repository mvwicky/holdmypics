from __future__ import annotations

from typing import Union

from loguru import logger
from PIL import Image, ImageDraw
from PIL.ImageFont import FreeTypeFont, ImageFont

from ..fonts import fonts
from .utils import FontParams, TextArgs, px_to_pt

MAX_TEXT_HEIGHT = 0.9
MAX_TEXT_WIDTH = 0.9


def guess_font_size(
    size: tuple[int, int], font_name: str
) -> tuple[Union[ImageFont, FreeTypeFont], int]:
    """Try and figure out the correct font size for a given height and font.

    Args:
        ``size``: The dimensions of the image in pixels.
        ``font_name``: The name of the font we're using.

    Returns:
        A size and an index.
    """
    height = size[1]
    # Don't want text to take up 100% of the height.
    height_prime = height * MAX_TEXT_HEIGHT
    pt_height = int(px_to_pt(int(height_prime)))  # The image height in points.
    font = fonts[font_name]
    if pt_height in font:
        # If this point value is an actual font size, return it.
        idx = fonts.font_sizes.index(pt_height)
        logger.debug("Returning {0} with size {1} ({2})", font_name, pt_height, idx)
        return font[pt_height], idx
    s_mod = pt_height - (pt_height % 4)
    if s_mod in font:
        idx = fonts.font_sizes.index(s_mod)
        logger.debug("Returning {0} with size {1} ({2})", font_name, s_mod, idx)
        return font[s_mod], idx
    if pt_height > fonts.max_size:
        logger.debug(
            "Returning {0} with size {1} ({2})",
            font_name,
            fonts.max_size,
            len(fonts.font_sizes) - 1,
        )
        return font[fonts.max_size], len(fonts.font_sizes) - 1
    elif pt_height < fonts.min_size:
        logger.debug("Returning {0} with size {1} (0)", font_name, fonts.min_size)
        return font[fonts.min_size], 0
    last = fonts.font_sizes[0]
    for i, sz in enumerate(fonts.font_sizes[1:]):
        if last < pt_height < sz:
            logger.debug("Returning {0} with size {1} ({2})", font_name, sz, i)
            return font[sz], i
    i = len(fonts.font_sizes) - 1
    sz = fonts.font_sizes[-1]
    logger.debug("Returning {0} with size {1} ({2})", font_name, sz, i)
    return font[sz], i


def get_font(d: ImageDraw.ImageDraw, sz: tuple[int, int], args: TextArgs) -> FontParams:
    """Get the correctly sized font for the given image size and text.

    Args:
        d: An ImageDraw instance
        sz: The height and width of the output image
        args: The text parameters
    """
    font, idx = guess_font_size(sz, args.font_name)
    tsize = d.textsize(args.text, font)
    face = fonts[args.font_name]
    while tsize >= sz and idx > 0:  # Make the text as small as possible
        idx -= 1
        font_size = fonts.font_sizes[idx]
        font = face[font_size]
        tsize = d.textsize(args.text, font)
    logger.debug("Ended up with size {0}", fonts.font_sizes[idx])
    return FontParams(font, tsize)


def draw_text(im: Image.Image, args: TextArgs) -> Image.Image:
    w, h = im.size
    d = ImageDraw.Draw(im)
    font, (tw, th) = get_font(d, (int(w * 0.9), h), args)
    logger.info('Writing text "{0}" (size={1})', args.text, (tw, th))
    tc = int((w - tw) / 2), int((h - th) / 2)
    anchor = "lt" if "\n" not in args.text else "la"
    d.text(tc, args.text, font=font, fill=args.color, align="center", anchor=anchor)
    if args.debug:
        d.rectangle(
            (tc, (int((w + tw) / 2), int((h + th) / 2))), outline="#000", width=3
        )
    return im
