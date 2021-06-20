from __future__ import annotations

import functools
import random
from string import hexdigits
from typing import NamedTuple

from loguru import logger
from PIL.ImageFont import ImageFont

from ..constants import PX_PER_PT


class FontParams(NamedTuple):
    font: ImageFont
    size: tuple[int, int]


class TextArgs(NamedTuple):
    color: str
    text: str
    font_name: str
    debug: bool


RAND_COLOR = "rand".casefold()


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


@functools.lru_cache(maxsize=128)
def get_color(color: str) -> str:
    start = int(color.startswith("#"))
    color = color[start:].casefold()
    if not all(e in hexdigits for e in color):
        logger.warning("Unable to create hex color from `{0}`", color)
        return color
    n = len(color)
    if n in (3, 4):
        color = "".join(c * 2 for c in color)
    if len(color) == 6:
        color = "".join((color, "ff"))
    if len(color) in (3, 4, 6, 8):  # Should only be 8
        return "".join(("#", color))
    logger.warning("Unable to create hex color from `{0}`", color)
    return color


def resolve_color(col: str) -> str:
    col = col.casefold()
    col = col if col != RAND_COLOR else random_color()
    return get_color(col)
