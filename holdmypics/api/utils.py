from __future__ import annotations

import functools
import random
from string import hexdigits
from typing import NamedTuple, Union

from loguru import logger
from PIL.ImageFont import FreeTypeFont, ImageFont

from ..constants import PX_PER_PT


class FontParams(NamedTuple):
    font: Union[ImageFont, FreeTypeFont]
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
    return "".join(f"{random.randrange(1 << 8):02x}" for _ in range(3))


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
        logger.warning("Unable to create hex color from {0!r}", color)
        return color
    n = len(color)
    if n in (3, 4):
        color = "".join(c * 2 for c in color)
        n *= 2
    if n == 6:
        color = f"{color}ff"
    if len(color) in (3, 4, 6, 8):  # Should only be 8
        return f"#{color}"
    logger.warning("Unable to create hex color from {0!r}", color)
    return color


def convert_color(
    color: Union[float, tuple[float, ...], str]
) -> tuple[float, float, float, float]:
    raise NotImplementedError


def resolve_color(col: str) -> str:
    col = col.casefold()
    col = col if col != RAND_COLOR else random_color()
    return get_color(col)
