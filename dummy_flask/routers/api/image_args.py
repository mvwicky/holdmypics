from typing import Optional

import attr

from ..._types import Dimension


def clamp_alpha(a: float) -> float:
    return max(0.0, min(float(a), 1.0))


@attr.s(slots=True, auto_attribs=True, frozen=True)
class ImagePathArgs(object):
    size: Dimension
    bg_color: str = "cef"
    fg_color: str = "555"
    fmt: str = "png"


@attr.s(slots=True, auto_attribs=True, frozen=True)
class ImageQueryArgs(object):
    text: Optional[str] = None
    filename: Optional[str] = None
    font_name: str = "overpass"
    dpi: int = 72
    alpha: float = attr.ib(default=1.0, converter=clamp_alpha)
